import gradio as gr
from gradio import ChatMessage
import random as rd
from prototype import gemini_generate_search_terms as gen


class Interface:
    def __init__(self):
        self.demo = gr.ChatInterface(self.output, type="messages")

    def output(self, message, history):
        history.append(ChatMessage(role="user", content=message))
        generated_search_terms = gen.generate_search_terms(message)

        return f"Your search terms are: {generated_search_terms}"

    def run(self):
        self.demo.launch()


