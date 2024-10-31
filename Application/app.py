import gradio as gr
from gradio import ChatMessage
import random as rd
from retriever import do_search
from prototype import gemini_generate_search_terms as gen


class Interface:
    def __init__(self, isTest=False):

        self.isTest = isTest
        if self.isTest:
            self.demo = gr.ChatInterface(self.outputTest, type="messages")
        else:
            self.demo = gr.ChatInterface(self.output, type="messages")

    def output(self, message, history):
        history.append(ChatMessage(role="user", content=message))
        articles = do_search(message)
        results = []

        for a in articles:
            results.append(a["title"])

        return f"Your search results are: {results}"

    def outputTest(self, message, history):
        history.append(ChatMessage(role="user", content=message))
        generated_search_terms = gen.generate_search_terms(message)

        return f"Your search terms are: {generated_search_terms}"

    def run(self):
        self.demo.launch()


