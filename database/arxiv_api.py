import arxiv
from arxiv import Client
import asyncio

client: Client = None

def get_arxiv_articles(query: str, max_results: int) -> list[dict]:
	global client
	if client is None:
		client = arxiv.Client(page_size=100)
	for i in range(3):
		try:
			search = arxiv.Search(
				query = query,
				max_results = max_results,
				sort_by = arxiv.SortCriterion.Relevance
			)
			break
		except Exception as e:
			print("Arxiv error occured, retrying: %s" % e)
			if i == 2:
				raise

	results = client.results(search)
	list_results = []
	for result in list(results):
		dict = {
			"title": result.title,
			"abstract": result.summary,
			"link": result.entry_id,
		}
		list_results.append(dict)
  
	print("done axriv func")
	return list_results