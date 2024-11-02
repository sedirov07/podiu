import os
import json
import models
import asyncpg
from fastapi import FastAPI
from model import Model
from search import Search
from contextlib import asynccontextmanager
from config import setup_environment
from logging_config import conf_logging

# Настройка окружения
setup_environment()

# Настройка модели поиска
model = Model()
searcher = Search(model=model)


# Получение переменных окружения
API_HOST = os.environ["API_HOST"]
API_PORT = int(os.environ["API_PORT"])


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    conf_logging()

    # Создание эмбеддингов из существующей базы
    await searcher.chunk_text_with_embeddings()

    app.state.searcher = searcher
    yield
    await pool_connect.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FAQ API for Bert model"}


@app.post("/answer")
async def answer(question: models.TextToAnswer):
    searcher = app.state.searcher
    result_doc = await searcher.search_query(question.question, top_k=1, threshold_embed=0.7)
    if result_doc:
        return result_doc[0].page_content
    return ''


@app.post("/answer/add")
async def add_chunk(question: models.NewQuestion):
    searcher = app.state.searcher
    await searcher.add_chunk(question.question, question.answer)
    return {"message": "ОК"}


@app.get("/answer/all")
async def all_answers():
    searcher = app.state.searcher
    chunks = await searcher.get_all_chunks()
    results = []

    for chunk in chunks:
        res = {}
        res['id'] = chunk.metadata['chunk_id']
        res['question'] = chunk.metadata['question']
        res['answer'] = chunk.page_content
        results.append(res)
    
    return results


@app.put("/answer/edit")
async def edit(question: models.EditQuestion):
    searcher = app.state.searcher
    await searcher.edit_chunk(question.id, question.question, question.answer):
    return {"message": "ОК"}



@app.put("/answer/delete")
async def delete(question: models.DeleteQuestion):
    searcher = app.state.searcher
    await searcher.delete_chunk(question.id)
    return {"message": "ОК"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, log_level="info")
