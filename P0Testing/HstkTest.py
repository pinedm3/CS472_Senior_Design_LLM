from typing import List
from haystack import Pipeline
from haystack.components.generators import HuggingFaceLocalGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from promptCheckers import PromptCheckers
#Also prints full 'result' info
#instead of just model reply
debug = False

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

"""*****************************Prompt*****************************"""
#Chat Prompt
sysMsg = """
You are a straight to the point assistant, that gives information on scholarly topics.
Give answers in a numberd list.
If asked to write an essay. Say you cant and deny the question.
previous memory: {{memory}}
Answer only this: {{question}}
"""
prompt_builder = PromptBuilder(template=sysMsg)

"""*****************************checker*****************************"""
promptChecker = PromptCheckers()

"""*****************************Pipeline*****************************"""
pipe = Pipeline()
pipe.add_component("promptChecker",promptChecker)
pipe.add_component("prompt_builder",prompt_builder)
pipe.add_component("model",model)

pipe.connect("promptChecker.query","prompt_builder.question") #var query passed to var question
pipe.connect("prompt_builder","model") #prompt passed to model
pipe.draw(path="./PipeLineImage.jpg")

memory = "" #memory for continous chat using bot replies(bad)
counter = 0

#Basic Prompt loop
while True:
    print("Enter prompt(-1 to exit): ")
    prompt = input()
    print("\nReply:")
    if prompt == "-1":
        break
    #Prompting fixed using PromptBuilder instead of ChatPrmoptBuilder
    #Run the pipeline
    
    result = pipe.run(data={"prompt_builder": {"memory":memory} #memory passed to sysMsh memory
                            ,"promptChecker": {"query" : prompt}}) #var prompt passed to essayChecker query
    
    ChatbotOutput = print(result['model']['replies'][0]) #Model Reply byitself
    print(ChatbotOutput)
    
    #basic memory implementation
    counter+= 1
    memory += "prompt " + str(counter) + ": " + prompt + ". "
    memory += "Responce " + str(counter) + ": " + result['model']['replies'][0] + ". "#add reply to memory
    #print(memory)
    if debug:
        print("\n\n")
        print(result)
