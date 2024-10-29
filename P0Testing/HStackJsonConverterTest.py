import json
from haystack.components.converters import JSONConverter
from haystack.dataclasses import ByteStream
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever

#Converts json file into hystack document


with open("serapiResponce.json", 'r') as file:
	textResponce = json.load(file)
    

docStore = InMemoryDocumentStore(embedding_similarity_function="cosine")

#Haystack required steps for conversions
info = ByteStream.from_string(json.dumps(textResponce))
converter = JSONConverter(jq_schema=".organic_results[]",content_key="title",extra_meta_fields={"snippet","position","link","publication"})

converterResults = converter.run(sources=[info])

#PIPELINE CODE

#p = Pipeline()
#p.add_component("converter",converter)
#pipeResults = p.run(data = {"converter": {"sources": [ByteStream.from_string(json.dumps(textResponce))] }})
#Capture information in haystack document form
#print(results)
documents = converterResults['documents']


document_embedder = SentenceTransformersDocumentEmbedder(model="intfloat/e5-large-v2", prefix="passage", meta_fields_to_embed={"link","publication","position"})
document_embedder.warm_up()

docEmbbed = document_embedder.run(documents)["documents"]
docStore.write_documents(docEmbbed)

docPrepPipeLine = Pipeline()
docPrepPipeLine.add_component("text_embedder", SentenceTransformersTextEmbedder(model="intfloat/e5-large-v2", prefix="passage"))
docPrepPipeLine.add_component("retriever", InMemoryEmbeddingRetriever(document_store=docStore))
docPrepPipeLine.connect("text_embedder.embedding", "retriever.query_embedding")

query = "Automated Malware Analysis"
result = docPrepPipeLine.run({"text_embedder": {"text": query}})

print(result['retriever']['documents'][0])


#Text file representation of document contents
"""
with open("JsonConverterResponce.txt","w") as file:
	for i in range(0,documents.__len__()):
		file.write("Search " + str(i) + ": \n")
		file.write("	Title: "+ "%s" % documents[i].content + "\n")
		for t in documents[i].meta:
			file.write("		%s" % t + ": " + "%s" % documents[i].meta[t]+"\n")
	file.write("\n")
"""