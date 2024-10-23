import tensorflow
from pandas import read_csv, DataFrame
from sentence_transformers import SentenceTransformer

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