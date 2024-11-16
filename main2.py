from retriever.retriever import do_embedding_based_search
import gradio as gr

study_type_list = [
	"Adaptive Clinical Trial",
	"Address",
	"Autobiography",
	"Bibliography",
	"Biography",
	"Case Reports",
	"Classical Article",
	"Clinical Conference",
	"Clinical Study",
	"Clinical Trial",
	"Clinical Trial, Phase I",
	"Clinical Trial, Phase II",
	"Clinical Trial, Phase III",
	"Clinical Trial, Phase IV",
	"Clinical Trial Protocol",
	"Clinical Trial, Veterinary",
	"Collected Work",
	"Comment",
	"Comparative Study",
	"Congress",
	"Consensus Development Conference",
	"Consensus Development Conference, NIH",
	"Controlled Clinical Trial",
	"Corrected and Republished Article",
	"Dataset",
	"Dictionary",
	"Directory",
	"Duplicate Publication",
	"Editorial",
	"Electronic Supplementary Materials",
	"English Abstract",
	"Equivalence Trial",
	"Evaluation Study",
	"Expression of Concern",
	"Festschrift",
	"Government Publication",
	"Guideline",
	"Historical Article",
	"Interactive Tutorial",
	"Interview",
	"Introductory Journal Article",
	"Journal Article (Default value when no more descriptive PT is provided or assigned)",
	"Lecture",
	"Legal Case",
	"Legislation",
	"Letter",
	"Meta-Analysis",
	"Multicenter Study",
	"News",
	"Newspaper Article",
	"Observational Study",
	"Observational Study, Veterinary",
	"Overall",
	"Patient Education Handout",
	"Periodical Index",
	"Personal Narrative",
	"Portrait",
	"Practice Guideline",
	"Preprint",
	"Pragmatic Clinical Trial",
	"Published Erratum",
	"Randomized Controlled Trial",
	"Randomized Controlled Trial, Veterinary",
	"Research Support, American Recovery and Reinvestment Act",
	"Research Support, N.I.H., Extramural",
	"Research Support, N.I.H., Intramural",
	"Research Support, Non-U.S. Gov't",
	"Research Support, U.S. Gov't, Non-P.H.S.",
	"Research Support, U.S. Gov't, P.H.S.",
	"Retracted Publication",
	"Retraction of Publication",
	"Review",
	"Scientific Integrity Review",
	"Systematic Review",
	"Technical Report",
	"Twin Study",
	"Validation Study",
	"Video-Audio Media",
	"Webcast",
]

age_range_list = [
	"Child: birth-18 years",
	"Newborn: birth-1 month",
	"Infant: birth-23 months",
	"Infant: 1-23 months",
	"Preschool Child: 2-5 years",
	"Child: 6-12 years",
	"Adolescent: 13-18 years",
	"Adult: 19+ years",
	"Young Adult: 19-24 years",
	"Adult: 19-44 years",
	"Middle Aged + Aged: 45+ years",
	"Middle Aged: 45-64 years",
	"Aged: 65+ years",
	"80 and over: 80+ years",
]

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

def set_filters(input):
	pubmed_filters = ["Publication Date", "Study Type", "Age", "Sex", "Species", "Custom Filter"]
	arxiv_filters = []
	if input == "pubmed":
		return gr.CheckboxGroup(label="Optional Filters", choices = pubmed_filters, interactive = True)
	if input == "arxiv":
		return gr.CheckboxGroup(label="Optional Filters", choices = arxiv_filters, type = 'index')
	else:
		return gr.CheckboxGroup(label="Optional Filters", choices = [], type = 'index')

def generate_filter_publication(input):
	if 'Publication Date' in input:
		return gr.DateTime(label = "From", show_label = True, include_time = False, type = 'datetime', visible = True), gr.DateTime(label = "To", show_label = True, include_time = False, type = 'datetime', visible = True)
	else:
		return gr.DateTime(label = "From", show_label = True, include_time = False, type = 'datetime', visible = False), gr.DateTime(label = "To", show_label = True, include_time = False, type = 'datetime', visible = False)

def generate_filter_studytype(input):
	if 'Study Type' in input:
		return gr.Dropdown(label = "Study Type", choices = study_type_list, filterable = True, visible = True, interactive = True)
	else:
		return gr.Dropdown(label="Study Type", visible = False)

def generate_filter_age(input):
	if 'Age' in input:
		return gr.Dropdown(label = "Age Range", choices = age_range_list, filterable = True, visible = True, interactive = True)
	else:
		return gr.Dropdown(label = "Age Range", visible = False)

def generate_filter_sex(input):
	if 'Sex' in input:
		return gr.Radio(label = "Biological Sex", choices = ["Male", "Female"], visible = True, interactive = True)
	else:
		return gr.Radio(label = "Biological Sex", visible = False)

def generate_filter_species(input):
	if 'Species' in input:
		return gr.Radio(label = "Species", choices = ["Human", "Non-Human"], visible = True, interactive = True)
	else:
		return gr.Radio(label = "Species", visible = False)

def generate_filter_custom(input):
	if 'Custom Filter' in input:
		return gr.Textbox(label = "Custom Filter", placeholder = "Type filter here", show_label = True, visible = True, interactive = True)
	else:
		return gr.Textbox(label = "Custom Filter", visible = False)

with gr.Blocks() as demo:
	state = gr.State({})
	title = gr.Label(container=False, value="AI-Powered Research Assistant")
	dropdown = gr.Dropdown(label="Database Selection", choices=[("Arxiv - STEM Articles", "arxiv"), ("PubMed - Medical Literature", "pubmed")], value="arxiv")

	with gr.Row():
		with gr.Column(scale = 1):
			enabled_filters = gr.CheckboxGroup(label = "Optional Filters")
			dynamic_filters = [gr.Radio(visible = False), gr.Dropdown(visible = False), gr.Textbox(visible = False)]
			dropdown.change(fn = set_filters, inputs = dropdown, outputs = enabled_filters, api_name = False)
		with gr.Column(scale = 2):
			with gr.Row():
				publication_date = [gr.DateTime(visible=False), gr.DateTime(visible=False)]
			with gr.Row():
				with gr.Column(scale = 1):
					study_type = gr.Dropdown(visible = False)
				with gr.Column(scale = 1):
					age_range = gr.Dropdown(visible=False)
			with gr.Row():
				with gr.Column(scale = 1):
					sex_type = gr.Radio(visible = False)
				with gr.Column(scale = 1):
					species_type = gr.Radio(visible = False)
			with gr.Row():
				custom_filter = gr.Textbox(visible = False)

			enabled_filters.change(fn = generate_filter_publication, inputs = enabled_filters, outputs = publication_date)
			enabled_filters.change(fn = generate_filter_studytype, inputs = enabled_filters, outputs = study_type)
			enabled_filters.change(fn = generate_filter_age, inputs = enabled_filters, outputs = age_range)
			enabled_filters.change(fn = generate_filter_sex, inputs = enabled_filters, outputs = sex_type)
			enabled_filters.change(fn = generate_filter_species, inputs = enabled_filters, outputs = species_type)
			enabled_filters.change(fn = generate_filter_custom, inputs = enabled_filters, outputs = custom_filter)

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