import json
from haystack.components.converters import JSONConverter
from haystack.dataclasses import ByteStream
#Converts json file into hystack document


with open("serapiResponce.json", 'r') as file:
	textResponce = json.load(file)
    
#Haystack required steps for conversions
info = ByteStream.from_string(json.dumps(textResponce))
converter = JSONConverter(jq_schema=".organic_results[]",content_key="title",extra_meta_fields={"snippet","position","link","publication"})
results = converter.run(sources=[info])

#Capture information in haystack document form
documents = results["documents"]

#Text file representation of document contents
with open("JsonConverterResponce.txt","w") as file:
	for i in range(0,documents.__len__()):
		file.write("Search " + str(i) + ": \n")
		file.write("	Title: "+ "%s" % documents[i].content + "\n")
		for t in documents[i].meta:
			file.write("		%s" % t + ": " + "%s" % documents[i].meta[t]+"\n")
	file.write("\n")
