from serpapi import GoogleSearch

# Uses the Serpapi API to perform Google Scholar search
# Create a text file in the same folder and paste your Serpapi API key in it
# Get a Serpapi API key at https://serpapi.com/google-scholar-api
SERPAPI_API_KEY_FILE_PATH = "prototype/serpapi_api_key.txt"

with open(SERPAPI_API_KEY_FILE_PATH, 'r') as file:
	api_key = file.readline()

def do_search(query: str) -> list[dict]:
	
	print("Searching for: " + query)
	params = {
		"engine": "google_scholar",
		"q": query,
		"api_key": api_key
	}

	search = GoogleSearch(params)
	results = search.get_dict()
	
	if 'error' in results.keys():
		print("Error occured: %s" % (results['error']))
		return {}

	return results["organic_results"]