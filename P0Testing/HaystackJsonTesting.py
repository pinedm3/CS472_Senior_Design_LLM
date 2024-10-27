import json
from haystack.components.converters import JSONConverter
from haystack.dataclasses import ByteStream

with open("serapiResponce.json", 'r') as file:
	textResponce = json.load(file)
    

#print(textResponce)

info = ByteStream.from_string(json.dumps(textResponce))

converter = JSONConverter(jq_schema=".organic_results[]",content_key="snippet",extra_meta_fields={"title","position","link","publication"})
results = converter.run(sources=[info])
documents = results["documents"]
print(documents)