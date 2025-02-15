import os
import models
from fastapi import FastAPI
from model import embedder
from search import Searcher
from giga_model import GigaModel
from contextlib import asynccontextmanager
from config import setup_environment
from logging_config import conf_logging


# Настройка окружения
setup_environment()

# Получение переменных окружения
API_HOST = os.environ["API_MODEL_API_HOST"]
API_PORT = int(os.environ["API_MODEL_API_PORT"])
AUTH_KEY = os.environ["AUTH_KEY"]
SCOPE = os.environ["SCOPE"]
MODEL_NAME = os.environ["MODEL_NAME"]


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    conf_logging()
    # Настройка модели поиска
    searcher = await Searcher.create(model=embedder)
    giga_model = GigaModel(auth_key=AUTH_KEY, scope=SCOPE, model_name=MODEL_NAME, searcher=searcher)
    app.state.giga_model = giga_model
    yield
    await searcher.save_chunks()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FAQ API"}


@app.post("/get_answer")
async def answer(question: models.TextToAnswer):
    giga_model = app.state.giga_model
    giga_answer = await giga_model.get_rag_result(question)
    return giga_answer


@app.post("/answer/add_question")
async def add_chunk_question(question: models.NewQuestion):
    searcher = app.state.giga_model.searcher
    await searcher.add_chunk_question(question.question, question.answer)
    return {"message": "ОК"}


@app.post("/answer/add_chunk")
async def add_chunk_question(chunk: models.NewChunk):
    searcher = app.state.giga_model.searcher
    await searcher.add_chunk(chunk.text)
    return {"message": "ОК"}


@app.get("/answer/all_answers")
async def all_answers():
    searcher = app.state.giga_model.searcher
    chunks = await searcher.get_all_chunks()
    results = []

    for chunk in chunks:
        res = {}
        res['id'] = chunk.metadata['chunk_id']
        res['question'] = chunk.metadata.get('question', 'no question')
        res['answer'] = chunk.page_content
        results.append(res)
    
    return results


@app.put("/answer/edit_question")
async def edit(question: models.EditQuestion):
    searcher = app.state.giga_model.searcher
    await searcher.edit_chunk_question(question.id, question.question, question.answer)
    return {"message": "ОК"}


@app.put("/answer/edit_chunk")
async def edit(chunk: models.EditChunk):
    searcher = app.state.giga_model.searcher
    await searcher.edit_chunk(chunk.id, chunk.text)
    return {"message": "ОК"}


@app.put("/answer/delete_chunk")
async def delete(question: models.DeleteQuestion):
    searcher = app.state.giga_model.searcher
    await searcher.delete_chunk(question.id)
    return {"message": "ОК"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, log_level="info")
