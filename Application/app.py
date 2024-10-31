import gradio as gr
from gradio import ChatMessage
import random as rd
from retriever import do_search


class Interface:
    def __init__(self):
        self.demo = gr.ChatInterface(self.output, type="messages")

    def output(self, message, history):
        history.append(ChatMessage(role="user", content=message))
        articles = do_search(message)
        results = []

        for a in articles:
            results.append(a["title"])

        return f"Your search results are: {results}"

    def run(self):
        self.demo.launch()


