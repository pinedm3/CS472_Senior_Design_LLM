import gradio as gr


def inputPrompt(name):
    return "Hello " + name


demo = gr.Interface(fn=inputPrompt, inputs=gr.Textbox(), outputs="text")

demo.launch()

