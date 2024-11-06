from typing import List
from haystack import Pipeline
from haystack.components.generators import HuggingFaceLocalGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from promptCheckers import PromptCheckers
from seraApiTodocEmbbed import seraApiTodocEmbbed
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
#Also prints full 'result' info
#instead of just model reply
debug = False

"""*****************************promptMessages*****************************"""
sysMsg = """
You are a straight to the point assistant, that gives information on scholarly topics.
Give answers in a numberd list.
previous memory: {{memory}}
Answer question: {{question}}

"""
searchPrompt = """
You are a straight to the point assistant, that gives information on scholarly topics.
Using the returned results information: 
{% if documents != NoneType %}
    {% for document in documents %}
    
       {{ document.content }}
       {{ document.meta['title'] }}
       {{ document.meta['publication'] }}
        {{ document.meta['link'] }}
    {% endfor %}
{% endif %}
Answer this: {{question}}
"""
"""*****************************Model Info*****************************"""
#model args
KwargsDict = {
    "do_sample": True,
    "top_k": 4,
    "max_new_tokens": 300,
    "clean_up_tokenization_spaces": False
}
#running locally
model = HuggingFaceLocalGenerator(model="google/gemma-2-2b-it",generation_kwargs=KwargsDict)
"""*****************************Scholar PipeLine STUFF*****************************"""
#could also be doucment[0]

promptBuilder = PromptBuilder(template=searchPrompt)
#FILE will be document[i].contont -> which gives a 'snippit'
#             document[i].meta[title,publication,link,position(ranking)] will give other info(single str with "")
#searchApiPrompt = PromptBuilder(template=searchPrompt)
docStore = InMemoryDocumentStore(embedding_similarity_function="cosine")
docEmbedder = SentenceTransformersDocumentEmbedder(model="intfloat/e5-large-v2", prefix="passage", meta_fields_to_embed={"link","publication","position"}) #Embbeds document
docEmbedder.warm_up()
retriever = InMemoryEmbeddingRetriever(document_store=docStore)
docPrepPipeLine = Pipeline()
docPrepPipeLine.add_component("textEmbedder", SentenceTransformersTextEmbedder(model="intfloat/e5-large-v2", prefix="passage")) #embbeds query text
docPrepPipeLine.add_component("retriever", retriever)
docPrepPipeLine.connect("textEmbedder.embedding", "retriever.query_embedding")
docPrepPipeLine.draw(path="./scholarPipeline.jpg")
"""*****************************regularPipeline*****************************"""
"""
TODO: Either have pchecker query go to new scholar component. Which then will do an api request and grab query info.
      Which will then give the info to the prompt Checker.
        -IDEALLY scholar info gets put into front end and be interacted with
        -AND/OR PromptBuilder gets modifed to include necessary info that scholar api Returned
            Such as the title,snippit,publication, and link
                Would require either to give all search rankings or only the documet[0] or something similar
"""
"""*****************************checker*****************************"""

promptBuilder = PromptBuilder(template=searchPrompt)
regularPipe = Pipeline()
regularPipe.add_component("promptChecker",PromptCheckers())
regularPipe.add_component("promptBuilder",promptBuilder)
regularPipe.add_component("model",model)
#Scholar api connections

#var query passed to var question

regularPipe.connect("promptChecker.query", "promptBuilder.question")
regularPipe.connect("promptBuilder.prompt","model.prompt") #prompt passed to model
regularPipe.draw(path="./PipeLineImage.jpg")

memory = "" #memory for continous chat using bot replies(bad)
counter = 0
#******************************************************************************
ChatbotOutput = ""
#Basic Prompt loop
while True:
    print("Enter prompt(-1 to exit): ")
    prompt = input()
    print("\nReply:")
    if prompt == "-1":
        break
    
    queryType = PromptCheckers.typeOfQuery(prompt)
    #oneshot classifer detects whether search
    if  queryType["labels"][0] == 'search':
        print("Query is of search type")
        docStore.write_documents(seraApiTodocEmbbed(prompt,docEmbedder),policy='DuplicatePolicy.SKIP') #function call to to scholar search and return doc embedd     
    #Summary is just fallhback for now
    else:         
        print("Query is of other type")
    searchResult = docPrepPipeLine.run({"textEmbedder" : {"text" : prompt}})
    ChatbotDocumentOutput = searchResult['retriever']['documents']
    regResult = regularPipe.run(data={"promptBuilder":  {"template_variables": {"memory":memory, "documents": ChatbotDocumentOutput}} #memory passed to sysMsh memory
                        ,"promptChecker": {"query" : prompt} #var prompt passed to essayChecker query
                        }) 
    ChatbotOutput = regResult['model']['replies'][0] #Model Reply byitself
    counter+= 1
    
    #basic memory implementation
    memory += "Question_Asked number " + str(counter) + ": " + prompt + ". "
    memory += "Responce number " + str(counter) + ": " + regResult['model']['replies'][0] + ". "#add reply to memory
    
    print(ChatbotOutput)
