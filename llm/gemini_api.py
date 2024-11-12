import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Create a text file in the same folder and paste your Gemini API key in it
# Get a free Gemini API key at https://aistudio.google.com/app/apikey
GEMINI_API_KEY_FILE_PATH = "llm/gemini_api_key.txt"

with open(GEMINI_API_KEY_FILE_PATH, 'r') as file:
	api_key = file.readline()


# Generates content using Gemini given a prompt
# Lower temperature = more predictable, Higher temperature = more creative
def generate(prompt: str, temperature: float = 1.0) -> str:
	genai.configure(api_key=api_key)
	model = genai.GenerativeModel("gemini-1.5-flash")
	safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
		HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
		HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
	return model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temperature), safety_settings=safety_settings)


# Generates search terms given a user query, uses 0 temperature to be deterministic
def generate_search_terms(user_query: str, num_search_terms: int) -> list[str]:
	prompt = "You are a research assistant. Generate the %s best search queries that can be used to retrieve scholarly articles that can help the user research the following topic: \n %s\n Respond with only the search terms separated by newlines." % (str(num_search_terms), user_query)
	response = generate(prompt, 0)
	search_queries = response.text.replace("\"","").split("\n")
	search_queries = search_queries[:num_search_terms]
	return search_queries