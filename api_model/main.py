import os
import json
import models
import asyncpg
from fastapi import FastAPI
from contextlib import asynccontextmanager
from faq_tb import FAQTable, get_keywords, get_intersections_count, kw_model
from config import setup_environment
from logging_config import conf_logging

# Настройка окружения
setup_environment()

# Получение переменных окружения
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
API_HOST = os.environ["API_HOST"]
API_PORT = int(os.environ["API_PORT"])


async def create_pool():
    return await asyncpg.create_pool(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    conf_logging()

    pool_connect = await create_pool()
    data_base = FAQTable(pool_connect)
    await data_base.init_insert()

    app.state.data_base = data_base
    yield
    await pool_connect.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FAQ API for Bert model"}


@app.post("/answer")
async def answer(question: models.TextToAnswer):
    keyword = get_keywords(question.question, kw_model)
    data_base = app.state.data_base

    res = await data_base.get_answers()

    keywords = list(map(lambda x: json.loads(x['keywords']), res))
    possible_indexes = []

    for i in range(len(keywords)):
        counter = get_intersections_count(keyword, keywords[i])
        if counter > 0:
            possible_indexes.append((counter, i))

    possible_indexes = sorted(possible_indexes, key=lambda x: x[0], reverse=True)
    result = []

    for index in possible_indexes:
        result.append({'question': res[index[1]]['question'], 'answer': res[index[1]]['answer']})
    if result:
        return result[0]['answer']

    return ''


@app.post("/answer/add")
async def add(question: models.NewQuestion):
    data_base = app.state.data_base
    await data_base.add_answer(question)
    return {"message": "ОК"}


@app.get("/answer/all")
async def all_answers():
    data_base = app.state.data_base
    res = await data_base.get_all_answers()
    return res


@app.put("/answer/edit")
async def edit(question: models.EditQuestion):
    data_base = app.state.data_base
    await data_base.edit_answer(question)
    return {"message": "ОК"}


@app.put("/keywords/edit")
async def kw_edit(question: models.EditKeywords):
    data_base = app.state.data_base
    await data_base.edit_keywords(question)
    return {"message": "ОК"}


@app.put("/answer/delete")
async def delete(question: models.DeleteQuestion):
    data_base = app.state.data_base
    await data_base.delete_answer(question.id)
    return {"message": "ОК"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, log_level="info")
