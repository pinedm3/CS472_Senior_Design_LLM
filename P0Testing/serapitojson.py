
import json
import requests


API_KEY_FILE = 'serpapi_api_key.txt'
with open(API_KEY_FILE, 'r') as file:
	api_key = file.readline()
 
url = "https://www.searchapi.io/api/v1/search"
query = "Nueroscience"
params = {
  "engine": "google_scholar",
  "q": query,
  "api_key": api_key
}

response = requests.get(url, params = params)
file = open("serapiResponce.txt","a")
file.write(response.json)
