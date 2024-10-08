from haystack.components.generators.chat import HuggingFaceLocalChatGenerator
from haystack.dataclasses import ChatMessage
from transformers import AutoModelForCausalLM, GenerationConfig


#args
KwargsDict = {
    "do_sample": True,
    "top_k": 4,
    "max_new_tokens": 80
}

generator = HuggingFaceLocalChatGenerator(model="Qwen/Qwen2-0.5B",generation_kwargs=KwargsDict)
generator.warm_up()


#Input
debug = False

while True:
    print("Enter prompt: ")
    prompt = input()
    if prompt == "-1":
        break
    messages = [ChatMessage.from_user(prompt)]
    result = generator.run(messages)    
    print(result["replies"][0].content)

if debug:
    print("\n\n")
    print(result)
    


