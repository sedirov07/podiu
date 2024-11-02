from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn.functional as F


class Model:
    def __init__(self, tokenizer=None, model=None):
        if no tokenizer:
            tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        if not model:
            model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    
        self.tokenizer = tokenizer
        self.model = model

    def get_embedding(self, sentence):
        def mean_pooling(model_output, attention_mask):
            token_embeddings = model_output[0]
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        # Tokenize sentence
        encoded_input = self.tokenizer(sentence, padding=True, truncation=True, return_tensors='pt', max_length=512)

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform pooling
        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings

    def get_similarity(self, sentences):
        embedding1 = self.get_embedding(sentences[0])
        embedding2 = self.get_embedding(sentences[1])
        embedding1_np = embedding1.cpu().numpy()
        embedding2_np = embedding2.cpu().numpy()
        return cosine_similarity(embedding1_np, embedding2_np)[0][0]


# Load model from HuggingFace Hub
# tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
# model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

# transformer = Model(tokenizer, model)

# Sentences we want sentence embeddings for
# sentences = ['This is an example sentence', 'Each sentence is converted']

# print("Sentence embeddings:")
# similarity_score = transformer.get_similarity(sentences)
# print(similarity_score)
