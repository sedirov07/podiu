import os
import pickle
import aiofiles
from logging_config import conf_logging
from langchain.docstore.document import Document


conf_logging()


class Searcher:
    def __init__(self, model):
        self.model = model
        self.last_chunk_id = 0
        self.documents = []
        self.chunks = []

    @classmethod
    async def create(cls, model):
        instance = cls(model)
        if not os.path.exists('cache/chunks.pkl'):
            await instance.load_questions()
            await instance.chunk_text_with_embeddings()
        else:
            async with aiofiles.open('cache/chunks.pkl', 'rb') as file:
                data = await file.read()
                instance.chunks = pickle.loads(data)
                instance.last_chunk_id = max([c.metadata['chunk_id'] for c in instance.chunks])
        return instance
    
    async def load_questions(self, text_data=None):
        # Открываем файл и читаем его содержимое
        if not text_data:
            with open('data2.txt', 'r', encoding='utf-8') as file:
                text_data = file.read()
        
        # Разделяем текст на вопросы и ответы
        parts = text_data.split('?\n')
        questions = []
        answers = []
        
        for i in range(1, len(parts)):
            question = parts[i-1].split('\n')[-1].strip()
            if i == len(parts) - 1:
                answer = parts[i].strip()
            else:
                answer = '\n'.join(parts[i].split('\n')[:-1]).strip()
            questions.append(question + '?')
            answers.append(answer)
            
        for i, (question, answer) in enumerate(zip(questions, answers)):
            metadata = {
                "question": question,
                "chunk_id": i,
            }
        
            doc = Document(page_content=answer, metadata=metadata)
            self.documents.append(doc)
        
        if not self.chunks:
            self.chunks = self.documents

    async def save_chunks(self):
        async with aiofiles.open('cache/chunks.pkl', 'wb') as file:
            await file.write(pickle.dumps(self.chunks))
    
    async def chunk_text_with_embeddings(self):
        last_chunk_id = 0
        for chunk in self.chunks:
            chunk_text = chunk.page_content
            # question = chunk.metadata['question']
            last_chunk_id = max(last_chunk_id, chunk.metadata['chunk_id'])
            
            embedding = await self.model.get_embedding(f'search_document: {chunk_text}')
            chunk.metadata['embedding'] = embedding
            
        self.last_chunk_id = last_chunk_id
    
    async def add_chunk_question(self, question, answer, chunk_id=None):
        if not chunk_id or chunk_id in [c.metadata['chunk_id'] for c in self.chunks]:
            chunk_id = self.last_chunk_id + 1
            self.last_chunk_id += 1

        embedding = await self.model.get_embedding(f'search_document: {answer}')
        metadata = {
            "question": question,
            "chunk_id": chunk_id,
            "embedding": embedding
        }

        doc = Document(page_content=answer, metadata=metadata)
        self.chunks.append(doc)

    async def add_chunk(self, text, chunk_id=None):
        if not chunk_id or chunk_id in [c.metadata['chunk_id'] for c in self.chunks]:
            chunk_id = self.last_chunk_id + 1
            self.last_chunk_id += 1

        embedding = await self.model.get_embedding(f'search_document: {text}')
        metadata = {
            "chunk_id": chunk_id,
            "embedding": embedding
        }

        doc = Document(page_content=text, metadata=metadata)
        self.chunks.append(doc)
    
    async def delete_chunk(self, chunk_id):
        for i, chunk in enumerate(self.chunks):
            cur_chunk_id = chunk.metadata['chunk_id']
            if cur_chunk_id == chunk_id:
                self.chunks.pop(i)
                break
                
    async def edit_chunk(self, chunk_id, text):
        await self.delete_chunk(chunk_id)
        await self.add_chunk(text, chunk_id)

    async def edit_chunk_question(self, chunk_id, question, answer):
        await self.delete_chunk(chunk_id)
        await self.add_chunk_question(question, answer, chunk_id)
    
    async def get_chunk(self, chunk_id):
        for i, chunk in enumerate(self.chunks):
            cur_chunk_id = chunk.metadata['chunk_id']
            if cur_chunk_id == chunk_id:
                return self.chunks[i]
        return {Document(page_content='', metadata={'chunk_id': 0, 'question': '', 'embedding': [[]]})}
    
    async def get_all_chunks(self):
        return self.chunks
    
    async def search_query(self, query, top_k=0, threshold_embed=0.5):
        query_embedding = await self.model.get_embedding(f'search_query: {query}')
        similarities = []
        
        for chunk in self.chunks:
            embedding = chunk.metadata['embedding']
            similarity = await self.model.get_similarity(query_embedding, embedding)
            if similarity >= threshold_embed:
                similarities.append((chunk, similarity))

        if not similarities:
            return []
        similarities.sort(key=lambda x: x[-1], reverse=True)
        
        if top_k:
            return similarities[:top_k]
        
        return similarities
