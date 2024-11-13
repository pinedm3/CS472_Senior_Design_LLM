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


def do_embedding_based_search(query: str, num_search_terms: int = 5, results_per_search: int = 25) -> dict:
    # Generate search terms
    print("Generating search terms...")
    search_terms: list[str] = generate_search_terms(query, num_search_terms)
    print("Search terms generated:")
    for term in search_terms:
        print(term)

    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

    # Store documents in a dictionary to prevent duplicates
    documents_dict = {}
    docList = []
    print("Getting articles...")

    # The articles will be retrieved in dictionary format (see database.py)
    # The embeddings will only be generated from Title and Abstract, the rest of the fields will be metadata
    # Hacky method to select what database to search for testing purposes
    database = 1
    if database == 1:
        for term in search_terms:
            for article in get_arxiv_articles(term, results_per_search):
                #documents_dict[article["title"]] = Document(content="Title:%s\nAbstract:%s" % (article["title"], article["abstract"]), meta=article)
                docList.append(Document(content=article["abstract"], meta={"title": article["title"],"link": article["link"]}))

    elif database == 2:
        for term in search_terms:
            for article in get_pubmed_articles(term, results_per_search):
                docList.append(Document(content=article["abstract"], meta={"title": article["title"],"link": article["link"]}))

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
    #ndexing_pipeline.run({"documents": list(documents_dict.values())})
    indexing_pipeline.run({"documents": docList})

    print("Searching for articles...")
    result = query_pipeline.run({"text_embedder":{"text": query}})

    return result['retriever']['documents']

# Example usage
# from retriever import do_search
# do_search("Find some articles on software engineering", 5)
# will return a list of dictionaries, each dictionary will have fields such as "title", "abstract", etc.
# see database.py for more info