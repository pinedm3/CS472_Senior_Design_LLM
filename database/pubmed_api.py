from pymed import PubMed

def instantiate_pubmed_object(toolname: str = None, email: str = None) -> PubMed:
    pubmed_connection = PubMed(tool = toolname, email = email)
    return pubmed_connection

def get_pubmed_articles(pubmed, query: str, max_results: int) -> list[dict]:
    result = pubmed.query(query, max_results)

    list_results = []
    for article in list(result):
        links = article.pubmed_id.split()
        dict = {
            "title": article.title,
            "abstract": article.abstract,
            "link": 'https://pubmed.ncbi.nlm.nih.gov/' + links[0],
            "full_link_list": links
        }
        list_results.append(dict)
    return list_results