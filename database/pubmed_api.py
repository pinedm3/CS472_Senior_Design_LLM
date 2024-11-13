import pymed
from pymed import PubMed

pubmed_connection: PubMed = None

def get_pubmed_articles(query: str, max_results: int) -> list[dict]:
    global pubmed_connection
    if pubmed_connection == None:
        pubmed_connection = PubMed(tool="AI Article Search Tool")
    
    result = pubmed_connection.query(query, max_results)
    list_results = []
    for article in list(result):
        dict = {
            "title": article.title,
            "abstract": article.abstract,
            "link": article.pubmed_id,
        }
        list_results.append(dict)
    return list_results