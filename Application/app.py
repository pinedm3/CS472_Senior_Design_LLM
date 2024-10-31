import gradio as gr
from gradio import ChatMessage
import random as rd
from retriever import do_search


class Interface:
    def __init__(self):
        self.demo = gr.ChatInterface(self.output, type="messages")

    def output(self, message, history):
        history.append(ChatMessage(role="user", content=message))
        result = do_search(message)

        return f"Your search results are: {result}"

    def run(self):
        self.demo.launch()


