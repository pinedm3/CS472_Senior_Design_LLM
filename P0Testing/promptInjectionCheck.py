from haystack import component
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
#@component
#class InjectionCheck:
"""
Check for prompt injection
"""
  #@component.output_types(query=str) #outputs
#def run(self, query:str): #Inputs
#prompt = query  
tokenizer = AutoTokenizer.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
model = AutoModelForSequenceClassification.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")

classifier = pipeline(
"text-classification",
model=model,
tokenizer=tokenizer,
truncation=True,
max_length=512,
device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
)


while True:
    print("input(-1 to exit): ")
    query = input()
    if(query == -1):
        break
    result = classifier(query)
    label = result[0]['label']
    print(result)
    if(label == "INJECTION"):
        print("illegal prompt deteted.\nReprompt.")
        continue
    elif(label == "SAFE"):
        continue
    

    
    #return {"query": prompt}
    
       
