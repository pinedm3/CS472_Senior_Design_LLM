from pymed import PubMed

client: PubMed

def get_pubmed_articles(pubmed, query: str, max_results: int) -> list[dict]:
    global client
    if client is None:
        client = PubMed()
          
    result = client.query(query, max_results)

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