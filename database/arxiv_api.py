import arxiv

def get_articles(query: str, max_results: int) -> list[dict]:
	client = arxiv.Client()
	search = arxiv.Search(
		query = query,
		max_results = max_results,
		sort_by = arxiv.SortCriterion.Relevance
	)
	results = client.results(search)
	list_results = []
	for result in list(results):
		dict = {
			"title": result.title,
			"abstract": result.summary,
			"link": result.entry_id,
		}
		list_results.append(dict)
	return list_results