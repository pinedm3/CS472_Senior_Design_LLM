# py -m pip install transformers[tf] --upgrade
# py -m pip install tensorflow
# py -m pip instal sentence-transformers
# py -m pip install numpy
# py -m pip install -U six numpy wheel packaging
# py -m pip install -U keras_preprocessing --no-deps
# py -m pip install tokenizers

# https://medium.com/@ceejayiwufitness/exploring-bert-and-sbert-for-sentence-similarity-2e7d151ce690

import tensorflow
import pandas
import numpy
import torch
from pandas import read_csv, DataFrame
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from tokenizers import BertWordPieceTokenizer


# import keras_nlp


class TFSentenceTransformer(tensorflow.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(TFSentenceTransformer, self).__init__()
        self.model = SentenceTransformer('sentence-transformers/msmarco-roberta-base-v2')

    def call(self, encoded_inputs, normalize=True):
        model_output = self.model(input_ids=encoded_inputs["input_ids"],
                                  attention_mask=encoded_inputs["attention_mask"],
                                  token_type_ids=encoded_inputs.get("token_type_ids"))
        embeddings = self.mean_pooling(model_output, encoded_inputs["attention_mask"])
        if normalize:
            embeddings = self.normalize(embeddings)
        return embeddings

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = tensorflow.cast(tensorflow.broadcast_to(
            tensorflow.expand_dims(attention_mask, -1),
            tensorflow.shape(token_embeddings)
        ),
            tensorflow.float32
        )
        return tensorflow.math.reduce_sum(token_embeddings * input_mask_expanded, axis=1) / tensorflow.clip_by_value(
            tensorflow.math.reduce_sum(input_mask_expanded, axis=1), 1e-9, tensorflow.float32.max)

    def normalize(self, embeddings):
        embeddings, _ = tensorflow.linalg.normalize(embeddings, 2, axis=1)
        return embeddings


class E2ESentenceTransformer(tensorflow.keras.Model):
    def __init__(self, model_name_or_path, **kwargs):
        super().__init__()
        self.tokenizer = tensorflow.keras.models.BertTokenizer(model_name_or_path, **kwargs)
        self.model = TFSentenceTransformer(model_name_or_path, **kwargs)

    def call(self, inputs):
        tokenized = self.tokenizer(inputs)
        return self.model(tokenized)


def parseDataframe(path_to_file, fill_new_or_append: int, dataframe: DataFrame = None, maintain_column_count=True,
                   keep_header=2):
    if fill_new_or_append != 1 and fill_new_or_append != 2:
        raise ValueError("fill_or_append must equal 1 (Fill) or 2 (Append)")

    if keep_header == 2:
        new_data = read_csv(path_to_file)
    elif keep_header == 1:
        new_data = read_csv(path_to_file, header=None)
    elif keep_header == 0:
        new_data = read_csv(path_to_file, header=None)
        new_data = new_data.iloc[1:]
    else:
        raise ValueError(
            "keep_header must equal 0 (Ignore header and delete first row), 1 (No header), or 2 (Keep and use header)")

    if fill_new_or_append == 1:
        return new_data
    else:
        new_frame = DataFrame()
        for column_name in new_data.columns:
            if column_name in dataframe.columns:
                new_frame[column_name] = pandas.concat([new_data[column_name], dataframe[column_name]], axis=0,
                                                       ignore_index=True)
            elif column_name not in dataframe and maintain_column_count is False:
                new_frame[column_name] = new_data[column_name]
        return new_frame


def dropAllExcept(dataframe: DataFrame, kept_columns: list[str]):
    for column in dataframe.columns:
        if column not in kept_columns:
            dataframe.drop(labels=column, axis='columns', inplace=True)
    return dataframe


# data = parseDataframe('latest_research_articles.csv', 1)
# data = parseDataframe('phys_and_computsci_articles.csv', 2, data)

# data = dropAllExcept(data, ["title", "abstract"])
# data.to_csv('Combined_Dataset.csv')
# print(data)

# tokenizer = BertWordPieceTokenizer(

#    clean_text = False,
#    handle_chinese_chars = False,
#    strip_accents = False,
#    lowercase = False,
# )

# files = ['Combined_Dataset.csv']

# tokenizer.train(
#    files,
#    vocab_size = 2500,
#    min_frequency = 3,
#    show_progress = True,
#    #special_tokens = ['[PAD]', '[UNK]', '[CLS]', '[sep]', '[MASK]'],
#    limit_alphabet = 10000,
#    wordpieces_prefix = '##'
# )
# tokenizer.add_tokens(['[SEP]'])
# tokenizer.save_model('.')

# create a BERT tokenizer with trained vocab
vocab = 'vocab.txt'
# tokenizer = BertWordPieceTokenizer(vocab)

# test the tokenizer with some text
# encoded = tokenizer.encode('...')
# print(encoded.tokens)


# model_id = 'sentence-transformers/all-MiniLM-L6-v2'
# e2e_model = E2ESentenceTransformer(model_id)

Pepe = TFSentenceTransformer()
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/msmarco-roberta-base-v2')
model = AutoModel.from_pretrained('sentence-transformers/msmarco-roberta-base-v2')


def run_model(payload: list[str]):
    encoded_input = tokenizer(payload, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)

    embeddings = Pepe.mean_pooling(model_output, encoded_input["attention_mask"])
    similarity = cosine_similarity([embeddings[0], embeddings[1]])
    norm_similarity = (similarity[1][0] + 1) / 2
    return norm_similarity


def test_model(test_strings: list[str]):
    similarity = run_model(test_strings)
    print("Sentences:" + test_strings[0] + " / " + test_strings[1])
    print(f"Similarity Score: {similarity}")


payload = ["This is a sentence embedding", "This is another sentence embedding"]
test_model(payload)
payload_2 = ["This is a sentence embedding", "This is another potato with some cheese and basil"]
test_model(payload_2)

# print(f"Output Shape: {payload_encoded.shape}")
# print(f"Prediction: {prediction}")
# e2e_model.summary()

# encoded_input = tokenizer(payload, padding = True, truncation = True, return_tensors = 'tf')
# sentence_embedding = model(encoded_inputs = encoded_input)

# print(sentence_embedding.shape)

