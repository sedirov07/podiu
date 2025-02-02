from sentence_transformers import SentenceTransformer


class Model:
    def __init__(self, model):
        self.model = model

    async def get_embedding(self, sentence):
        embeddings = self.model.encode(sentence, convert_to_tensor=False)
        return embeddings

    @staticmethod
    async def get_similarity(embedding1, embedding2):
        sim_score = embedding1 @ embedding2.T
        return sim_score


# Load model from HuggingFace Hub
model = SentenceTransformer("ai-forever/ru-en-RoSBERTa")

embedder = Model(model=model)

# Sentences we want sentence embeddings for
# sentences = ['This is an example sentence', 'Each sentence is converted']

# print("Sentence embeddings:")
# similarity_score = transformer.get_similarity(sentences)
# print(similarity_score)
