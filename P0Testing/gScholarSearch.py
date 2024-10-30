import json
import requests
from haystack.components.converters import JSONConverter
from haystack.dataclasses import ByteStream

#More direct implementation of scholar search
#Writes responce to file to test and not use search limit
def gScholarSearch(query:str) -> any:
  API_KEY_FILE = 'serpapi_api_key.txt'
  with open(API_KEY_FILE, 'r') as file:
    api_key = file.readline()
  
  url = "https://www.searchapi.io/api/v1/search"
  params = {
    "engine": "google_scholar",
    "q": query,
    "api_key": api_key
  }

#Commented out to save api requests
  #response = requests.get(url, params = params)
  #file = open('serapiResponce.json','w')
  #file.write(response.text)

  with open("serapiResponce.json", 'r') as file:
      textResponce = json.load(file)


  #Json to haystack document converter
  #Haystack required steps for conversions
  #info = ByteStream.from_string(json.dumps(response.json()))
  info = ByteStream.from_string(json.dumps(textResponce))
                                
  converter = JSONConverter(jq_schema=".organic_results[]",content_key="title",extra_meta_fields={"snippet","position","link","publication"})
  converterResults = converter.run(sources=[info])
  
  #Text file representation of document contents
  return converterResults['documents']