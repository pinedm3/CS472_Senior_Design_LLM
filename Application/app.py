import gradio as gr
import random as rd


def random_Yes_No(message, history):
    return rd.choice(["Yes", "No"])


demo = gr.ChatInterface(random_Yes_No)

demo.launch()

