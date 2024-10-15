from typing import List
from haystack import Pipeline
from haystack.components.generators import HuggingFaceLocalGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from SentenceSimTest import EssayChecker
#Also prints full 'result' info
#instead of just model reply
debug = False


"""*****************************Model Info*****************************"""
#model args
KwargsDict = {
    "do_sample": True,
    "top_k": 4,
    "max_new_tokens": 200,
    "clean_up_tokenization_spaces": False
}
#running locally
model = HuggingFaceLocalGenerator(model="google/gemma-2-2b-it",generation_kwargs=KwargsDict)

"""*****************************Prompt*****************************"""
#Chat Prompt
sysMsg = """
You are a friendly assistant that only gives schorlarly articles on a given topic.
Give straight to the point answers.
Give answers in a numberd list.
Do not give answers unless asked.
If asked to write an essay. Say you cant and deny the question.
If you cant undestand a question. ask for a new question.
previous memory: {{memory}}
Answer only this: {{question}}
"""
prompt_builder = PromptBuilder(template=sysMsg)
"""*****************************checker*****************************"""
checker = EssayChecker()

"""*****************************Pipeline*****************************"""
pipe = Pipeline()
pipe.add_component("essayChecker", checker)
pipe.add_component("prompt_builder",prompt_builder)
pipe.add_component("model",model)
pipe.connect("prompt_builder","model")
#pipe.draw(path="./P0Testing.jpg")

memory = "" #memory for continous chat using bot replies(bad)
counter = 0
#Basic Prompt loop for testing
while True:
    print("Enter prompt(-1 to exit): ")
    prompt = input()
    print("\nReply:")
    if prompt == "-1":
        break
    #Prompting fixed using PromptBuilder instead of ChatPrmoptBuilder
    result = pipe.run(data={"prompt_builder": {"question":prompt,"memory":memory}
                            ,"essayChecker": {"query" : prompt}}) #Run the pipeline
    print(result['model']['replies'][0])
    counter+= 1
    memory += "Question_Asked number " + str(counter) + ": " + prompt + ". "
    memory += "Responce number " + str(counter) + ": " + result['model']['replies'][0] + ". "#add reply to memory
    #print(memory)
    if debug:
        print("\n\n")
        print(result)
