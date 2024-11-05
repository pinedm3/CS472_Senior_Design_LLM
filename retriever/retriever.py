# !pip install haystack-ai
# !pip install sentence-transformers>=3.0.0

from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack import Document
from haystack import Pipeline

from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from sentence_transformers import SentenceTransformer
from database.arxiv_api import get_articles
from llm.gemini_api import generate_search_terms


def do_embedding_based_search(query: str, num_search_terms: int = 5, results_per_search: int = 25) -> list[dict]:
    # Generate search terms
    print("Generating search terms...")
    search_terms: list[str] = generate_search_terms(query, num_search_terms)
    print("Search terms generated:")
    for term in search_terms:
        print(term)

    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

    # Store documents in a dictionary to prevent duplicates
    documents_dict = {}
    print("Getting articles...")

    # The articles will be retrieved in dictionary format (see database.py)
    # The embeddings will only be generated from Title and Abstract, the rest of the fields will be metadata
    for term in search_terms:
        for article in get_articles(term, results_per_search):
            documents_dict[article["title"]] = Document(content="Title:%s\nAbstract:%s" % (article["title"], article["abstract"]), meta=article)
    
    # This model can be replaced with the path to Tyler's SBERT model when it's ready
    model = "BAAI/bge-small-en-v1.5"
    document_embedder = SentenceTransformersDocumentEmbedder(model=model)
    text_embedder = SentenceTransformersTextEmbedder(model=model)

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component("embedder", document_embedder)
    indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
    indexing_pipeline.connect("embedder", "writer")

    query_pipeline = Pipeline()
    query_pipeline.add_component("text_embedder", text_embedder)
    query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store, scale_score=True))
    query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

    print("Indexing articles...")
    indexing_pipeline.run({"documents": list(documents_dict.values())})

    print("Searching for articles...")
    result = query_pipeline.run({"text_embedder":{"text": query}})

    article_results = []
    for r in result['retriever']['documents']:
        article = r.meta
        article["score"] = r.score
        article_results.append(article)
    return article_results

# Example usage
# from retriever import do_search
# do_search("Find some articles on software engineering", 5)
# will return a list of dictionaries, each dictionary will have fields such as "title", "abstract", etc.
# see database.py for more info