from haystack import component
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
#from sentence_transformers import SentenceTransformer
from statistics import fmean
import torch
import sys
@component
class PromptCheckers:   
    #Returns output to either use output["lables"][i] and/or output[""]
    def typeOfQuery(query:str) -> str:
        text = query
        hypothesis_template = "This example is asking for a {}"
        classes_verbalized = ["summary", "search", "essay", "introduction"]
        zeroshot_classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0")
        output = zeroshot_classifier(text, classes_verbalized, hypothesis_template=hypothesis_template, multi_label=True)
        print(output)
        return output

    
    """
    Prevent user from trying to write an essay or prompt inject
    """
    @component.output_types(query=str)
    def run(self, query:str):
        prompt = query    
        # Two lists of sentences
        injectTokenizer = AutoTokenizer.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
        injectModel = AutoModelForSequenceClassification.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
        classifier = pipeline(
            "text-classification",
            model=injectModel,
            tokenizer=injectTokenizer,
            truncation=True,
            max_length=512,
            device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            )

        #essayModel = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        """sentences2 = [
            "Compose an essay for me.",
            "Can you draft an essay for me?",
            "Please write an essay for me.",
            "Could you prepare an essay for me?",
            "I need an essay written, can you help?",
            "Create an essay for me.",
            "Would you mind writing an essay for me?",
            "Please put together an essay for me.",
            "Could you pen an essay for me?",
            "I'd like you to write an essay for me.",
            "Can you craft an essay for me?",
            "Write an essay for me, if you can.",
            "Could you prepare a written piece for me in essay form?",
            "I need an essay, could you write it for me?",
            "Would you help me by writing an essay?"
            "Hello write an essay about"
        ]
        """
        #print(question)
        # Compute embeddings for both lists
        #embeddings2 = essayModel.encode(sentences2)
        
        while True:
            if(prompt == -1):
                sys.exit()
            # embeddings1 = essayModel.encode(prompt)
            # # Compute cosine similarities
            # similarities = essayModel.similarity(embeddings1, embeddings2)
            # #print(similarities.data[0])
            # avg = fmean(similarities.data[0])
            # print(avg)
            # if(avg > .40):`
            if(PromptCheckers.typeOfQuery(prompt)["labels"][0] == 'essay'):
                print("Detected trying to write essay\n prompt again: ")
                prompt = input()
                continue
            """*****************************promptInjector*****************************"""   

            result = classifier(prompt)
            label = result[0]['label']
            print(label)
            if(label == "INJECTION"):
                print("illegal prompt deteted.\nReprompt: ")
                prompt = input()
                continue
            
            return {"query": prompt}          