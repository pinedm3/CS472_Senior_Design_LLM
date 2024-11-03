# !pip install haystack-ai
# !pip install sentence-transformers>=3.0.0

from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack import Document
from haystack import Pipeline

from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from sentence_transformers import SentenceTransformer
from database import get_articles


def do_search(query: str, max_results: int = 5) -> list[dict]:
    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

    documents = []
    print("Getting articles...")

    # The articles will be retrieved in dictionary format (see database.py)
    # The embeddings will only be generated from Title and Abstract, the rest of the fields will be metadata
    for article in get_articles():
        documents.append(Document(content="Title:%s\nAbstract:%s" % (article["title"], article["abstract"]), meta=article))

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
    query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
    query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

    print("Indexing articles...")
    indexing_pipeline.run({"documents": documents})

    print("Searching for articles...")
    result = query_pipeline.run({"text_embedder":{"text": query}})

    article_results = []
    for r in result['retriever']['documents'][:max_results]:
        article_results.append(r.meta)
    return article_results

# Example usage
# from retriever import do_search
# do_search("Find some articles on software engineering", 5)
# will return a list of dictionaries, each dictionary will have fields such as "title", "abstract", etc.
# see database.py for more info