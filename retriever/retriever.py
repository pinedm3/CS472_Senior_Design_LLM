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
import asyncio
import time 
#Chooses the exact database and runs appropiate function
async def dataBaseSelectionSearch(searchTerms : str, database: str, resultsPerSearch: int):
    preArticles = []
    docData = []
    #Data base selection:
    t0 = time.time()
    match database:
        case "arxiv":
             async with asyncio.TaskGroup() as tg:
                for term in searchTerms:
                    preArticles.append(tg.create_task(get_arxiv_articles(term, resultsPerSearch)))
                    
        case "pubmed":
             articles = await get_pubmed_articles(term, resultsPerSearch)
        case _:
            raise Exception("Invalid database %s" % database)
    
    for articles in preArticles:
        for doc in articles._result:
            docData.append(Document(content=doc["abstract"], meta={"title": doc["title"],"link": doc["link"]}))
    t1 = time.time()
    print("dBSS() took: ", t1-t0)
    return docData

def do_embedding_based_search(query: str, num_search_terms: int = 5, results_per_search: int = 25, database: str = "arxiv") -> list:
    
    # Generate search terms
    print("Generating search terms...")
    t0 = time.time()
    search_terms:  list[str] = generate_search_terms(query, num_search_terms)
    t1 = time.time()
    print("Took: %f. \nSearch terms generated:" % (t1-t0))
    
    
    #ASYNCIO SEARCH ARTICLES
    
    
    docList = asyncio.run(dataBaseSelectionSearch(search_terms,database,results_per_search))
    #APPEND seperated lists to one list
   
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
         
    
    print("Indexing articles...")
    indexing_pipeline.run({"documents": docList})
    
    result = query_pipeline.run({"text_embedder":{"text": query}})

    return result['retriever']['documents']

# Example usage
# from retriever import do_search
# do_search("Find some articles on software engineering", 5)
# will return a list of dictionaries, each dictionary will have fields such as "title", "abstract", etc.
# see database.py for more info