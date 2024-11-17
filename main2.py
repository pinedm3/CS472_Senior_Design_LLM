from retriever.retriever import do_embedding_based_search
import gradio as gr
import asyncio



def pre_search(prev_btn, next_btn, results):
	prev_btn.visible = False
	next_btn.visible = False
	results.visible = False
	return prev_btn, next_btn, results

def do_search(query: str, database: str):
	results = do_embedding_based_search(query)
	output_string: str = ""
	index = 1
	for result in results:
		percent_score = round(result.score * 100, 2)
		output_string += str(index) + ". %s (%s relevance)\n %s\n\n" % (result.meta["title"], str(percent_score) + "%", result.meta["link"])
		index += 1

	return gr.skip(), gr.Markdown(label="Search Results", container=True, visible=True, value=output_string)

def show_results(starting_index: int = 0, results_to_show: int = 10, results: dict  = {}):
	pass

with gr.Blocks() as demo:
	state = gr.State({})
	title = gr.Label(container=False, value="AI-Powered Research Assistant")
	dropdown = gr.Dropdown(label="Database Select", choices=[("Arxiv - STEM Articles", "arxiv"), ("PubMed - BioMedical Litarature", "pubmed")], value="arxiv")
	with gr.Row(equal_height=True):
		search_bar = gr.Textbox(container=False, placeholder="Ask a question.", max_lines=1)
		search_btn = gr.Button("Search", scale=0, min_width=80)
	results = gr.Markdown(visible=False)
	with gr.Row(equal_height=True):
		prev_btn = gr.Button("Previous Page", visible = False)
		next_btn = gr.Button("Next Page", visible = False)
	search_btn.click(fn=pre_search, inputs=[prev_btn, next_btn, results], outputs=[prev_btn, next_btn, results])
	search_btn.click(fn=do_search, inputs=[search_bar, dropdown], outputs=[search_bar, results])

demo.launch()