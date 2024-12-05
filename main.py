from retriever.retriever import do_embedding_based_search
from promptchecking.prompt_checkers import illegal_prompt_checker
from llm.gemini_api import generate_search_terms
import gradio as gr
import asyncio
 
results_per_page = 20

study_type_list = [
	"",
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
	"",
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

age_range_filter = {
	"": "",
	"Child: birth-18 years": "infant[mh] OR child[mh] OR adolescent[mh]",
	"Newborn: birth-1 month": "infant, newborn[mh]",
	"Infant: birth-23 months": "infant[mh]",
	"Infant: 1-23 months": "infant[mh:noexp]",
	"Preschool Child: 2-5 years": "child, preschool[mh]",
	"Child: 6-12 years": "child[mh:noexp]",
	"Adolescent: 13-18 years": "adolescent[mh]",
	"Adult: 19+ years": "adult[mh]",
	"Young Adult: 19-24 years": "\"young adult\"[mh]",
	"Adult: 19-44 years": "adult[mh:noexp]",
	"Middle Aged + Aged: 45+ years": "(middle aged[mh] OR aged[mh])",
	"Middle Aged: 45-64 years": "middle aged[mh]",
	"Aged: 65+ years": "aged[mh]",
	"80 and over: 80+ years": "aged, 80 and over[mh]",
}

subject_type = [
	"",
	"Computer Science (cs)",
	"Economics (econ)",
	"Electrical Engineering and Systems Science (eess)",
	"Mathematics (math)",
	"Quantitative Biology (q-bio)",
	"Quantitative Finance (q-fin)",
	"Statistics (stat)",
	"Physics (grp_physics)"
]

#def get_current_date():
#	current_date = datetime.now().date()
#	return current_date.strftime("%Y-%m-%d")

def do_search(query: str, database: str, state: dict, p_date_from, p_date_to, stu_type, age_r, sex_t, spe_type, cus_filter, sub):
	print("Checking for prompt injection...")
	if(illegal_prompt_checker(query,False) == "PROMPTINJECTION"):
		print("Prompt injection detected.")
		raise gr.Error("Reprompt with a proper query", 5,True,"Prompt Injection Detected")

	filter_string = ""
	if database == 'pubmed':
		if p_date_from is not None and p_date_from != "" and p_date_to is not None and p_date_to != "":
			filter_string += " AND " + str(p_date_from.year) + '/' + str(p_date_from.month) + '/' + str(p_date_from.day) + ':' + str(p_date_to.year) + '/' + str(p_date_to.month) + '/' + str(p_date_to.day) + "[dp]"
		if stu_type is not None and stu_type != "":
			filter_string += " AND " + str(stu_type) + "[pt]"
		if age_r is not None and age_r != "":
			age_r = age_range_filter[age_r]
			filter_string += " AND " + str(age_r)
		if sex_t is not None and sex_t != "":
			filter_string += " AND " + str(sex_t).lower() + "[mh]"
		if spe_type is not None and spe_type != "":
			if spe_type == "Non-Human":
				filter_text = "\"animals\"[mh:noexp]"
			elif spe_type == "Human":
				filter_text = "humans[mh]"
			else:
				filter_text = ""
			filter_string += " AND " + filter_text
		if cus_filter is not None and cus_filter != "":
			filter_string += " AND " + '(' + str(cus_filter) + ')'
	#a_date_from, a_date_to, sub, phr, cl, cus_filter_arxiv
	elif database == 'arxiv':
		#if a_date_from is not None and a_date_from != "" and a_date_to is not None and a_date_to != "":
		#	filter_string += "date_range: from " + str(a_date_from.year) + '-' + str(a_date_from.month) + '-' + str(a_date_from.day) + " to " + str(a_date_to.year) + '-' + str(a_date_to.month) + '-' + str(a_date_to.day) + ' AND '
		if sub is not None and sub != "":
			filter_string += "cat:" + str(sub) + ' AND '
		#if cl is not None and cl != "":
		#	if cl == 'Allow':
		#		cl = 'True'
		#	else:
		#		cl = 'False'
		#	filter_string += "include_cross_list: " + str(cl) + ' AND '
		#if cus_filter_arxiv is not None and cus_filter_arxiv != "":
		#	filter_string += '(' + str(cus_filter_arxiv) + ')' + " AND "
		#if phr is not None and phr != "":
		#	filter_string += "(\"" + str(phr) + "\")" + " AND "


	print(filter_string)

	state["results"] = do_embedding_based_search(query, filter_string, database=database)
	state["starting_index"] = 0
	return gr.skip(),  gr.Button(visible=True),  gr.Button(visible=True), state


def showKeywordsButton():
	return gr.Button(visible=True)


def showAccordion():
	return gr.Accordion(visible=True, open=False)


def getKeywords(query: str):
	keywordList = generate_search_terms(query, 10)
	outputString = ", ".join(keywordList)
	return outputString

def showKeywords(keywords: list):
	return gr.Textbox(visible=True)


def next_page(state: dict):
	if "starting_index" in state.keys():
		state["starting_index"] = min(state["starting_index"] + results_per_page, len(state["results"]))
	return state

def previous_page(state: dict):
	if "starting_index" in state.keys():
		state["starting_index"] = max(state["starting_index"] - results_per_page, 0)
	return state

def show_results(state: dict):
	output_string: str = ""
	starting_index = state["starting_index"]
	for i in range(starting_index, starting_index + results_per_page):
		if i >= len(state["results"]):
			break
		result = state["results"][i]
		percent_score = round(result.score * 100, 2)
		output_string += str(i + 1) + ". %s (%s relevance)<br>%s \n\n" % (result.meta["title"], str(percent_score) + "%", result.meta["link"])
	return gr.Markdown(label="Search Results", container=True, visible=True, value=output_string)

def set_filters(input):
	pubmed_filters = ["Publication Date", "Study Type", "Age", "Sex", "Species", "Custom Filter"]
	arxiv_filters = ["Subject"]
	print(input)
	if input == "pubmed":
		return gr.update(label="Optional Filters", choices = pubmed_filters, interactive = True, visible = True, value = None), gr.update(visible = True), gr.update(visible = False)
	if input == "arxiv":
		return gr.update(label="Optional Filters", choices = arxiv_filters, interactive = True, visible = True, value = None), gr.update(visible = False), gr.update(visible = True)
	else:
		return gr.update(label="Optional Filters", choices = []), gr.update(visible = True), gr.update(visible = False)

def generate_filter_publication(input):
	if 'Publication Date' in input:
		return gr.update(visible = True), gr.update(visible = True)
	else:
		return gr.update(visible = False, value = ""), gr.update(visible = False, value = "")


def generate_filter_studytype(input):
	if 'Study Type' in input:
		return gr.update(label = "Study Type", choices = study_type_list, filterable = True, visible = True)
	else:
		return gr.update(visible = False, choices = [""], value = "")

def generate_filter_age(input):
	if 'Age' in input:
		return gr.update(label = "Age Range", choices = age_range_list, filterable = True, visible = True, interactive = True)
	else:
		return gr.update(visible = False, choices = [""], value = "")

def generate_filter_sex(input):
	if 'Sex' in input:
		return gr.update(label = "Biological Sex", choices = ["" ,"Male", "Female"], visible = True, interactive = True)
	else:
		return gr.update(visible = False, choices = [""], value = "")

def generate_filter_species(input):
	if 'Species' in input:
		return gr.update(label = "Species", choices = ["", "Human", "Non-Human"], visible = True, interactive = True)
	else:
		return gr.update(visible = False, choices = [""], value = "")

def generate_filter_custom(input):
	if 'Custom Filter' in input:
		return gr.update(label = "Custom Filter", placeholder = "Type filter here", show_label = True, visible = True, interactive = True)
	else:
		return gr.update(visible = False, value = "")

def generate_filter_phrase(input):
	if 'Phrase' in input:
		return gr.update(label = "Exact Phrase Match", placeholder = "Type phrase", show_label = True, visible = True, interactive = True)
	else:
		return gr.update(visible = False, value = "")

def generate_filter_subject(input):
	if 'Subject' in input:
		return gr.update(label = "Subject", choices = subject_type, show_label = True, visible = True, interactive = True)
	else:
		return gr.update(visible = False, choices = [""], value = "")

def generate_filter_cross(input):
	if "Cross-Listing Preference" in input:
		return gr.update(label = "Cross-listing Preference", choices = ['Allow', 'Block'], show_label = True, visible = True, interactive = True, value = 'Allow', info = "Allows results cross-listed in multiple subjects. (Defaults to Allowed)")
	else:
		return gr.update(visible = False, choices = ['Allow'], value = 'Allow')


theme = gr.themes.Default().set(block_border_color="#9191A1", input_border_color_focus="*block_border_color", block_label_text_color="*block_border_color", checkbox_label_border_color="*block_border_color", checkbox_border_color="*block_border_color")


with gr.Blocks(theme=theme, css_paths="theming.css",fill_width=True) as demo:
	state = gr.State({})
	title = gr.Label(container=False, value="AI-Powered Research Assistant")
	dropdown = gr.Dropdown(label="Database Selection", choices=[("Arxiv - STEM Articles", "arxiv"), ("PubMed - Medical Literature", "pubmed")], value="arxiv")

	with gr.Row():
		with gr.Column(scale = 1):
			enabled_filters = gr.CheckboxGroup(label="Optional Filters", choices = ["Subject"], visible=True)
		with gr.Column(scale = 2, visible = False) as pubmed:
			with gr.Row():
				pubmed_publication_date_from = gr.DateTime(label = "From", show_label = True, include_time = False, type = 'datetime', visible = False)
				pubmed_publication_date_to = gr.DateTime(label = "To", show_label = True, include_time = False, type = 'datetime', visible = False)
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
				pubmed_custom_filter = gr.Textbox(visible = False)
		#["Publication Date", "Subject", "Phrase", "Custom Filter"]
		with gr.Column(scale = 2, visible = True) as arxiv:
			#with gr.Row():
				#arxiv_publication_date_from = gr.DateTime(label = "From", show_label = True, include_time = False, type = 'datetime', visible = False)
				#arxiv_publication_date_to = gr.DateTime(label = "To", show_label = True, include_time = False, type = 'datetime', visible = False)
			with gr.Row():
				with gr.Column(scale = 1):
					subject = gr.Dropdown(visible = False)
				#with gr.Column(scale = 1):
					#phrase = gr.Textbox(visible = False)
			#with gr.Row():
				#with gr.Column(scale = 1):
					#arxiv_custom_filter = gr.Textbox(visible=False)
				#with gr.Column(scale = 1):
					#cross_list = gr.Radio(visible = False)

	dropdown.change(fn=set_filters, inputs=dropdown, outputs=(enabled_filters, pubmed, arxiv))
	enabled_filters.change(fn = generate_filter_publication, inputs = enabled_filters, outputs = (pubmed_publication_date_from, pubmed_publication_date_to))
	#enabled_filters.change(fn = generate_filter_publication, inputs = enabled_filters, outputs = (arxiv_publication_date_from, arxiv_publication_date_to))
	enabled_filters.change(fn = generate_filter_studytype, inputs = enabled_filters, outputs = study_type)
	enabled_filters.change(fn = generate_filter_age, inputs = enabled_filters, outputs = age_range)
	enabled_filters.change(fn = generate_filter_sex, inputs = enabled_filters, outputs = sex_type)
	enabled_filters.change(fn = generate_filter_species, inputs = enabled_filters, outputs = species_type)
	enabled_filters.change(fn = generate_filter_subject, inputs = enabled_filters, outputs = subject)
	#enabled_filters.change(fn = generate_filter_phrase, inputs = enabled_filters, outputs = phrase)
	#enabled_filters.change(fn = generate_filter_cross, inputs = enabled_filters, outputs = cross_list)
	enabled_filters.change(fn = generate_filter_custom, inputs = enabled_filters, outputs = pubmed_custom_filter)
	#enabled_filters.change(fn = generate_filter_custom, inputs = enabled_filters, outputs = arxiv_custom_filter)

	with gr.Accordion("Testing", visible=False) as accordion:
		test = gr.Textbox(container=False, placeholder="Ask a question.")
	with gr.Row(equal_height=True):
		search_bar = gr.Textbox(container=False, placeholder="Ask a question.",)
		search_btn = gr.Button("Search", scale=0, min_width=80)
	with gr.Row():
		keyword_btn = gr.Button("Show Generated Keywords", visible=False, scale=0)
		keyword_bar = gr.Textbox(container=True, visible=False, label="Keywords", lines=2)
	results = gr.Markdown(visible=False)
	with gr.Row(equal_height=True):
		prev_page_btn = gr.Button("Previous", visible=False)
		next_page_btn = gr.Button("Next", visible=False)

	gr.on(
		triggers=[search_bar.submit,search_btn.click],
		fn=do_search, 
  		inputs=[search_bar, dropdown, state, pubmed_publication_date_from, pubmed_publication_date_to, study_type, age_range, sex_type, species_type, pubmed_custom_filter, subject],
    	outputs=[search_bar, next_page_btn, prev_page_btn, state],
     	queue=True,concurrency_limit="default"
    ).then(fn=show_results, inputs=[state], outputs=[results])

	gr.on(
		triggers=[search_bar.submit, search_btn.click],
		fn=showKeywordsButton,
		outputs=keyword_btn
	)

	gr.on(
		triggers=[search_bar.submit, search_btn.click],
		fn=showAccordion,
		outputs=accordion
	).then(fn=getKeywords, inputs=search_bar, outputs=test)

	next_page_btn.click(fn=next_page, inputs=state, outputs=state).then(fn=show_results, inputs=[state], outputs=[results])
	prev_page_btn.click(fn=previous_page, inputs=state, outputs=state).then(fn=show_results, inputs=[state], outputs=[results])
	keyword_btn.click(fn=getKeywords, inputs=search_bar, outputs=keyword_bar).then(fn=showKeywords,inputs=search_bar, outputs=keyword_bar)
demo.queue(max_size=15,default_concurrency_limit=6)

demo.launch()