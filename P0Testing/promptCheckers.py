from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
#from sentence_transformers import SentenceTransformer
import torch

 
#Returns output to either use output["lables"][i] and/or output[""]
def type_of_query(query:str) -> str:
    text = query
    hypothesis_template = "This example is asking for a {}"
    classes_verbalized = ["summary", "search", "essay", "introduction"]
    zeroshot_classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0")
    output = zeroshot_classifier(text, classes_verbalized, hypothesis_template=hypothesis_template, multi_label=True)
    print(output)
    return output

"""
Prevent user from trying to write an essay or prompt inject
Returns either "PROMPTINJECTION","PROMPTESSAY" or "CLEAN"
"""

def illegal_prompt_checker(query:str, search_essay: bool) -> str:
    prompt = query    
    # Two lists of sentences
    inject_tokenizer = AutoTokenizer.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
    inject_model = AutoModelForSequenceClassification.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
    classifier = pipeline(
        "text-classification",
        model=inject_model,
        tokenizer=inject_tokenizer,
        truncation=True,
        max_length=512,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
        )
    
    if(search_essay):
        if(type_of_query(prompt)["labels"][0] == 'essay'):
            print("is PROMPTESSAY")
            return "PROMPTESSAY"
    
        """*****************************promptInjector*****************************"""   
    result = classifier(prompt)
    label = result[0]['label']
    print(label)
    if(label == "INJECTION"):
        print("is PROMPTINJECTION")
        return "PROMPTINJECTION"

    return "CLEAN"
