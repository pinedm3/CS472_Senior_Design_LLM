from sentence_transformers import SentenceTransformer
from haystack import component,Pipeline
from statistics import fmean
import sys
@component
class EssayChecker:
  """
  Prevent user from trying to write an essay
  """
  @component.output_types(query=str)
  def run(self, query:str):
      
       # Two lists of sentences
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    question = query  
    sentences2 = [
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
    
    #print(question)
    # Compute embeddings for both lists
    embeddings2 = model.encode(sentences2)
    
    while True:
        embeddings1 = model.encode(question)
        # Compute cosine similarities
        similarities = model.similarity(embeddings1, embeddings2)
        #print(similarities.data[0])
        avg = fmean(similarities.data[0])
        print(avg)
        
        if(avg > .40):
            print("Detected trying to write essay\n prompt again: ")
            question = input()
        else:
            return {"query": question}
