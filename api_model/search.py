import re
from model import Model
from logging_config import conf_logging
from langchain.docstore.document import Document


conf_logging()


class Search:
    async def __init__(self, chunks, model):
        self.model = model
        self.last_chunk_id = 0
        self.documents = []
        if not self.documents:
            await self.load_questions()
        if not chunks:
            self.chunks = self.documents
    
    async def load_questions(self, text_data=None):
        # Открываем файл и читаем его содержимое
        if not text_data:
            with open('data2.txt', 'r', encoding='utf-8') as file:
                text_data = file.read()
        
        # Разделяем текст на вопросы и ответы
        parts = text.split('?')
        questions = []
        answers = []
        
        for i in range(len(parts) - 1):
            question = parts[i].strip() + '?'
            answer = parts[i + 1].strip()
            questions.append(question)
            answers.append(answer)
            
        for i, question, answer in enumerate(zip(question, answer)):
            metadata = {
                "question": question,
                "chunk_id": i,
            }
        
            doc = Document(page_content=answer, metadata=metadata)
            self.documents.append(doc)
    
    async def chunk_text_with_embeddings(self):
        last_chunk_id = 0
        for chunk in self.chunks:
            chunk_text = chunk.page_content
            question = chunk.metadata['question']
            last_chunk_id = max(last_chunk_id, chunk.metadata['chunk_id'])
            
            embedding = await self.model.get_embedding(question)            
            chunk.metadata['embedding'] = embedding
            
        self.last_chunk_id = last_chunk_id
    
    async def add_chunk(self, question, answer):
        chunk_id = self.last_chunk_id + 1
        embedding = await self.model.get_embedding(question)            
        metadata = {
            "question": question,
            "chunk_id": chunk_id,
            'embedding': embedding
        }

        doc = Document(page_content=answer, metadata=metadata)
        self.chunks.append(doc)
    
    async def del_chunk(self, chunk_id):
        for i, chunk in enumerate(self.chunks):
            cur_chunk_id = chunk.metadata['chunk_id']
            if cur_chunk_id == chunk_id:
                self.chunks.pop(i)
                break
                
    async def edit_chunk(self, chunk_id, question, answer):
        await self.del_chunk(chunk_id)
        await self.add_chunk(chunk_id, question, answer)
    
    async def get_chunk(self, chunk_id):
        for i, chunk in enumerate(self.chunks):
            cur_chunk_id = chunk.metadata['chunk_id']
            if cur_chunk_id == chunk_id:
                return self.chunks[i]
    
    async def search_query(self, query, top_k=0, threshold_embed=0.5):
        query_embedding = await self.model.get_embedding(query)
        similarities = []
        
        for chunk in self.chunks:
            embedding = chunk.metadata['embedding']
            similarity = await self.model.get_similarity([query_embedding, embedding])[0][0]
            if similarity >= threshold_embed:
                similarities.append((chunk, similarity))

        similarities.sort(key=lambda x: x[-1], reverse=True)
        
        if top_k:
            return similarities[:top_k]
        
        return similarities


# model = Model()
# chunker = Search(model=model)
# await chunker.chunk_text_with_embeddings()
