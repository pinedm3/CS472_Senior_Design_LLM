from haystack import Pipeline
from haystack.components.generators import HuggingFaceLocalGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.utils import Secret
#Also prints full 'result' info
#instead of just model reply
debug = False

#model args
KwargsDict = {
    "do_sample": True,
    "top_k": 4,
    "max_new_tokens": 200,
    "clean_up_tokenization_spaces": False
}

#running locally
model = HuggingFaceLocalGenerator(model="google/gemma-2-2b-it",generation_kwargs=KwargsDict)

#Chat Prompt
sysMsg = """
You are an assistant that gives straight to the point answers. 
Give answers in a numberd list
This is your memory: {{memory}}
user Question: {{question}}

Give a short friendly reply before an answer
"""
prompt_builder = PromptBuilder(template=sysMsg)
#Pipeline
pipe = Pipeline()
pipe.add_component("prompt_builder",prompt_builder)
pipe.add_component("model",model)
pipe.connect("prompt_builder","model")

memory = "" #memory for continous chat using bot replies(bad)

#Basic Prompt loop for testing
while True:
    print("Enter prompt(-1 to exit): ")
    prompt = input()
    print("\nReply:")
    if prompt == "-1":
        break
    #Prompting fixed using PromptBuilder instead of ChatPrmoptBuilder
    result = pipe.run(data={"prompt_builder": {"question":prompt,"memory":memory}}) #Run the pipeline
    print(result['model']['replies'][0])
    memory += result['model']['replies'][0] + " "#add reply to memory
    
    if debug:
        print("\n\n")
        print(result)