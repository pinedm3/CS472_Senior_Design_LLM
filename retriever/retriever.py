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
async def searchArticles(term : str, database: str, resultsPerSearch: int):
    articles = None
    docData = []
    #Data base selection:
    match database:
        case "arxiv":
             articles = get_arxiv_articles(term, resultsPerSearch)
        case "pubmed":
             articles = get_pubmed_articles(term, resultsPerSearch)
        case _:
            raise Exception("Invalid database %s" % database)
                    
    for article in articles:
        docData.append(Document(content=article["abstract"], meta={"title": article["title"],"link": article["link"]}))
    return docData

async def do_embedding_based_search(query: str, num_search_terms: int = 5, results_per_search: int = 25, database: str = "arxiv") -> list:
    # Generate search terms
    print("Generating search terms...")
        #Not sure if await matter
    t0 = time.time()
    search_terms: await list[str] = generate_search_terms(query, num_search_terms)
    t1 = time.time()
    print("Took: %f. \nSearch terms generated:" % (t1-t0))
    coros = []
    for term in search_terms:
        coros.append(searchArticles(term,database,results_per_search))
        print(term)
    print("Getting articles...")
    t0 = time.time()
    asycRecs = asyncio.gather(*coros)
    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

    # Store documents
    docList = []
    
    # The articles will be retrieved in dictionary format (see database.py)
    # The embeddings will only be generated from Title and Abstract, the rest of the fields will be metadata    for term in search_terms:
    
    # for term in search_terms:
    #     if database == "arxiv":
    #         for article in get_arxiv_articles(term, results_per_search):
    #             docList.append(Document(content=article["abstract"], meta={"title": article["title"],"link": article["link"]}))
    #     elif database == "pubmed":
    #         for article in get_pubmed_articles(term, results_per_search):
    #             docList.append(Document(content=article["abstract"], meta={"title": article["title"],"link": article["link"]}))
    #     else:
    #         raise Exception("Invalid database %s" % database)
    
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
        #before actually needed
    await asycRecs
    t1 = time.time()
    print("asycResults took: ", t1-t0)
    for indivList in asycRecs._result:
        docList+= indivList
    indexing_pipeline.run({"documents": docList})

    print("Searching for articles...")
    result = query_pipeline.run({"text_embedder":{"text": query}})

    return result['retriever']['documents']

# Example usage
# from retriever import do_search
# do_search("Find some articles on software engineering", 5)
# will return a list of dictionaries, each dictionary will have fields such as "title", "abstract", etc.
# see database.py for more info