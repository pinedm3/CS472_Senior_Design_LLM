import google.generativeai as genai
import os

# Create a text file in the same folder and paste your Gemini API key in it
# Get a free Gemini API key at https://aistudio.google.com/app/apikey
GEMINI_API_KEY_FILE_PATH = "prototype/gemini_api_key.txt"
MAX_SEARCH_TERMS = 3

with open(GEMINI_API_KEY_FILE_PATH, 'r') as file:
	api_key = file.readline()

def generate_search_terms(user_query: str, max_search_terms: int = 3) -> list[str]:
	print("Generating search terms...")
	# Generate Search terms
	genai.configure(api_key=api_key)

	model = genai.GenerativeModel("gemini-1.5-flash")
	
	prompt = "You are a research assistant. Generate the %s best search queries that can be input into Google Scholar to retrieve scholarly articles that can help the user research the following topic: \n %s\n Respond with only the search terms separated by newlines." % (str(max_search_terms), user_query)
	response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0))

	print("Prompt used: %s" % (prompt))

	search_queries = response.text.replace("\"","").split("\n")
	search_queries = search_queries[:MAX_SEARCH_TERMS]

	print("Search queries generated:")
	for query in search_queries:
		print(query)
	return search_queries