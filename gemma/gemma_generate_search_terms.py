from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import os

# Create a text file in the same folder and paste your HuggingFace Access Token in it
# https://huggingface.co/settings/tokens
HUGGINGFACE_ACCESS_TOKEN_FILE_PATH = "gemma/huggingface_access_token.txt"

with open(HUGGINGFACE_ACCESS_TOKEN_FILE_PATH, 'r') as file:
	access_token = file.readline()

def generate_search_terms(user_query: str, max_search_terms: int = 3) -> list[str]:
	login(token=access_token)

	tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b-it")

	# Download the model from HuggingFace
	model = AutoModelForCausalLM.from_pretrained(
		"google/gemma-2-9b-it",
		device_map="auto",
	)

	MAX_SEARCH_TERMS = 3

	prompt = "Generate the %s best search queries to input into Google Scholar to retrieve scholarly articles on the following topic: \n %s\n Respond with only the search terms separated by newlines." % (str(MAX_SEARCH_TERMS), user_query)
	input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")

	outputs = model.generate(**input_ids, max_new_tokens=100)

	raw_text = tokenizer.decode(outputs[0])
	search_queries = raw_text.replace("\"","").split("\n")
	return search_queries