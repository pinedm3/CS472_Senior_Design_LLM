import kagglehub
import pandas as pd


# Retrieves the articles from a Kaggle database as a list of dictionaries
# Each article has a "title", "abstract, "doi", etc.
# See https://www.kaggle.com/datasets/victornuez/latest-research-articles?select=phys_and_computsci_articles.csv for more info
def get_articles(max_articles: int = -1) -> list[dict]:
	path = kagglehub.dataset_download("victornuez/latest-research-articles")
	df = pd.read_csv(path + "/phys_and_computsci_articles.csv")
	if max_articles > 0:
		df = df.iloc[:max_articles]
	return df.to_dict(orient='records')