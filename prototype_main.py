#from prototype import google_scholar_search as search
from Application import app


# Example of utilizing the prototype code to generate search terms and search Google Scholar with them
# This is meant to be a simple prototype to give a rough idea of what our final product will do
# We will replace the Gemini API with a local model and the Serpapi API with a database + search model


UI = app.Interface(False)
UI.run()

"""user_query = input("Search: ")

generated_search_terms = gen.generate_search_terms(user_query)

all_results = []
for term in generated_search_terms:
    for result in search.do_search(term):
        all_results.append(result)

print("\n")
print("-----------------------------------------------")
for result in all_results:
    print(result["title"] + ": " + result["link"] + "\n")
"""