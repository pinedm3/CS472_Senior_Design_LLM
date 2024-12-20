# !pip install haystack-ai
# !pip install sentence-transformers>=3.0.0
from torch.cuda import is_available as is_cuda_available
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack import Document
from haystack import Pipeline

from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.utils import ComponentDevice, Device
from sentence_transformers import SentenceTransformer
from database.arxiv_api import get_arxiv_articles
from database.pubmed_api import get_pubmed_articles
from llm.gemini_api import generate_search_terms
import time 
import arxiv
import gradio as gr
#Chooses the exact database and runs appropiate function
def database_selection_search(search_terms : list[str], filter_string:str, database: str, results_per_search: int) -> list[Document]:
    pre_articles = []
    doc_data = []
    #Data base selection:
    t0 = time.time()

    combined_query = "("
    for term in search_terms:
        combined_query += "(" + term + ")"
        if term != search_terms[-1]:
            combined_query += " OR "

    if database == "arxiv":
        combined_query = filter_string + "all:" + combined_query + ')'
    elif database == "pubmed":
        combined_query += ')' + filter_string
    print("Combined queries: %s" % combined_query)



    match database:
        case "arxiv":
            print("Searching using Arxiv")
            for i in range(3):
                try:
                    pre_articles.append(get_arxiv_articles(combined_query, len(search_terms) * results_per_search))
                except arxiv.UnexpectedEmptyPageError as e:
                    print("Arxiv error occured, retrying: %s" % e)
                    if i == 2:
                        raise gr.Error("Arxiv search failed! Try searching again", title="Search Error")
                else:
                    break
        case "pubmed":
            print("Searching using PubMed")
            pre_articles.append(get_pubmed_articles(combined_query, len(search_terms) * results_per_search))
        case _:
            raise Exception("Invalid database %s" % database)
    print("Writing searched articles to document list...")    
    for articles in pre_articles:
        for doc in articles:
            doc_data.append(Document(content=doc["abstract"], meta={"title": doc["title"],"link": doc["link"]}))
    t1 = time.time()
    print("dBSS() took: ", t1-t0)
    print("Retrieved %s articles" % len(doc_data))
    return doc_data


#runs haystack pipeline and calss dataBaseSeclectionSearch
def do_embedding_based_search(query: str, filter_string: str, num_search_terms: int = 10, results_per_search: int = 15, database: str = "arxiv") -> dict:
    # Generate search terms
    print("Generating %s search terms..." % num_search_terms)
    t0 = time.time()
    search_terms:  list[str] = generate_search_terms(query, num_search_terms)
    t1 = time.time()
    print("Took: %f. \nSearch terms generated:" % (t1-t0))
    
    for term in search_terms:
        print(term)
    
    #ASYNCIO SEARCH ARTICLES
    doc_list = database_selection_search(search_terms, filter_string, database, results_per_search)
    t0 = time.time()
    
    # Store documents
    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
    model = "BAAI/bge-small-en-v1.5"

    # Use GPU if available
    device = ComponentDevice.from_single(Device.cpu())
    if is_cuda_available():
        device = ComponentDevice.from_single(Device.gpu(id=0))
    
    document_embedder = SentenceTransformersDocumentEmbedder(model=model, device=device)
    text_embedder = SentenceTransformersTextEmbedder(model=model, device=device)
    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component("embedder", document_embedder)
    indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store,policy='DuplicatePolicy.SKIP'))
    indexing_pipeline.connect("embedder", "writer")

    query_pipeline = Pipeline()
    query_pipeline.add_component("text_embedder", text_embedder)
    query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store, scale_score=True, top_k=num_search_terms*results_per_search))
    query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
         
    
    print("Running indexing pipeline...")
    indexing_pipeline.run({"documents": doc_list}) 
    result = query_pipeline.run({"text_embedder":{"text": query}})
    t1 = time.time()
    
    #Time might not be accurate due to await on doclist?
    print("after databaseSearch took: ", t1-t0)
    return {"results": result['retriever']['documents'], "search_terms": search_terms}

# Example usage
# from retriever import do_search
# do_search("Find some articles on software engineering", 5)
# will return a list of dictionaries, each dictionary will have fields such as "title", "abstract", etc.
# see database.py for more info