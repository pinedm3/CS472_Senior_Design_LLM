import gradio as gr
from gradio import ChatMessage
from gradio import Chatbot
import random as rd
from retriever.retriever import do_embedding_based_search

class Interface:
    def __init__(self, isTest=False):

        self.isTest = isTest
        if self.isTest:
            self.demo = gr.ChatInterface(self.outputTest, type="messages")
            self.demo.chatbot.placeholder = "<strong>Hello, welcome to the AI-Powered Research Assistant!</strong><br>To begin, describe your research question and I'll fetch scholarly articles that match that topic."
        else:
            self.demo = gr.ChatInterface(self.output, type="messages")

    def output(self, message, history):
        history.append(ChatMessage(role="user", content=message))
        results = do_embedding_based_search(message)

        output_string: str = ""
        index = 1
        for result in results:
            output_string += str(index) + ". %s\n %s\n" % (result["title"], result["link"])
            index += 1

        return output_string

    # def outputTest(self, message, history):
    #     history.append(ChatMessage(role="user", content=message))
    #     generated_search_terms = gen.generate_search_terms(message)

    #     all_results= []
    #     for term in generated_search_terms:
    #         for result in gs.do_search(term)[:4]:
    #             all_results.append(result)
        
    #     output_string: str = ""
    #     index = 1
    #     for result in all_results:
    #         output_string += str(index) + ". %s\n %s\n" % (result["title"], result["link"])



    #     return output_string

    def run(self):
        self.demo.launch()


