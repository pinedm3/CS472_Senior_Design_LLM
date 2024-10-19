from haystack import component
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import sys
@component
class InjectionCheck:
    """
    Check for prompt injection
    """
    @component.output_types(query=str) #outputs
    def run(self, query:str): #Inputs
        prompt = query
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
            if(prompt == -1):
                sys.exit()
            result = classifier(prompt)
            label = result[0]['label']
            print(label)
            if(label == "INJECTION"):
                print("illegal prompt deteted.\nReprompt: ")
                prompt = input()
                continue
            elif(label == "SAFE"):
                return {"query": prompt}  
        
