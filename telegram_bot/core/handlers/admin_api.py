import os
import aiohttp
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.utils.states_question_model import StepsQuestionModel
from core.keyboards.admin_api_kb import questions_actions_keyboard, create_paginated_keyboard
from core.translate.translator import del_translation_text


API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")


async def get_all_questions_api() -> list[dict]:
    api = f"http://{API_HOST}:{API_PORT}/answer/all"
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            if response.status == 200:
                return await response.json()
            return [{'error response': str(response)}]


async def edit_question_api(q_id, new_question, new_answer) -> bool:
    api = f"http://{API_HOST}:{API_PORT}/answer/edit"
    async with aiohttp.ClientSession() as session:
        async with session.put(api, json={"id": q_id, "question": new_question, "answer": new_answer}) as response:
            return response.status == 200


async def add_question_api(new_question, new_answer) -> bool:
    api = f"http://{API_HOST}:{API_PORT}/answer/add"
    async with aiohttp.ClientSession() as session:
        async with session.post(api, json={"question": new_question, "answer": new_answer}) as response:
            return response.status == 200


async def delete_question_api(q_id) -> bool:
    api = f"http://{API_HOST}:{API_PORT}/answer/delete"
    async with aiohttp.ClientSession() as session:
        async with session.put(api, json={"id": q_id}) as response:
            return response.status == 200


async def edit_keywords_api(q_id, new_keywords) -> bool:
    api = f"http://{API_HOST}:{API_PORT}/keywords/edit"
    async with aiohttp.ClientSession() as session:
        async with session.put(api, json={"id": q_id, "keywords": new_keywords}) as response:
            return response.status == 200


async def handle_pagination(call: CallbackQuery):
    data = call.data
    if data.startswith('page_'):
        page = int(data.split('_')[1])
        questions_list = await get_all_questions_api()
        questions_kb = await create_paginated_keyboard(questions_list, page)
        await call.message.edit_reply_markup(reply_markup=questions_kb)
    elif data == 'cancel_action':
        await call.message.delete()


# Получение всех вопросов для выбора действия
async def change_questions_model(message: Message, page: int = 1):
    questions_list = await get_all_questions_api()
    questions_kb = await create_paginated_keyboard(questions_list, page)
    await message.answer('Выберите вопрос:', reply_markup=questions_kb)


# Получение возможных действи с вопросами
async def get_question_action_model(call: CallbackQuery, state: FSMContext):
    q_id = int(call.data.split('_')[-1])
    questions = await get_all_questions_api()
    question = ''
    answer = ''

    for quest in questions:
        if q_id == int(quest['id']):
            question = quest['question']
            answer = quest['answer']
            break

    await call.message.edit_text(f'Выбран вопрос:\n{question}\nВыберите действие:',
                                 reply_markup=questions_actions_keyboard)
    await state.update_data(q_id=q_id, questions=questions, question=question, answer=answer)
    await state.set_state(StepsQuestionModel.GET_ACTION)


# Просмотр ответа
async def get_answer_model(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answer = data['answer']

    await call.message.answer(answer, reply_markup=admin_menu_keyboard)
    await state.clear()


# Изменение вопроса
async def change_question_model(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_id = data['q_id']
    questions = data['questions']
    question = data['question']
    answer = data['answer']
    question_dict = {}
    for quest in questions:
        if q_id == int(quest['id']):
            question_dict = quest

    await call.message.answer(f'*Текущий вопрос:*\n{question}\n'
                              f'*Текущий ответ:*\n{answer}\n'
                              f'*Введите новый вопрос:*')

    await state.update_data(question_dict=question_dict)
    await state.set_state(StepsQuestionModel.GET_NEW_QUESTION)


# Получение нового вопроса для изменения
async def get_new_edit_question_model(message: Message, state: FSMContext):
    new_question = message.text
    await message.answer('Введите новый ответ:')
    await state.update_data(new_question=new_question)
    await state.set_state(StepsQuestionModel.GET_NEW_ANSWER)


# Получение нового ответа для изменения
async def get_new_edit_answer_model(message: Message, state: FSMContext):
    data = await state.get_data()
    question_dict = data.get('question_dict')
    question = data.get('question')
    answer = data.get('answer')
    q_id = int(question_dict['id'])
    new_question = data.get('new_question')
    new_answer = message.text

    await edit_question_api(q_id=q_id, new_question=new_question, new_answer=new_answer)
    await del_translation_text(answer)
    await del_translation_text(question)
    await message.answer(f"*Вопрос*\n{question}\nизменен на\n{new_question}\n"
                         f"*Ответ*\n{answer}\nизменен на\n{new_answer}", reply_markup=admin_menu_keyboard)
    await state.clear()


# Запрос на добавление нового вопроса
async def add_question_model(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите новый вопрос:')
    await state.set_state(StepsQuestionModel.GET_NEW_QUESTION_ADD)


# Добавление нового вопроса
async def add_new_question_model(message: Message, state: FSMContext):
    new_question = message.text
    await message.answer('Введите новый ответ:')
    await state.update_data(new_question=new_question)
    await state.set_state(StepsQuestionModel.GET_NEW_ANSWER_ADD)


# Добавление нового ответа
async def add_new_answer_model(message: Message, state: FSMContext):
    data = await state.get_data()
    new_question = data.get('new_question')
    new_answer = message.text
    await add_question_api(new_question=new_question, new_answer=new_answer)
    await message.answer(f"*Вопрос:*\n{new_question}\nдобавлен.", reply_markup=admin_menu_keyboard)
    await state.clear()


# Удаление вопроса
async def delete_question_model(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_id = data["q_id"]
    question = data['question']
    answer = data['answer']
    if await delete_question_api(q_id=q_id):
        await del_translation_text(question)
        await del_translation_text(answer)
        await call.message.answer(f'*Вопрос* {question} удален.', reply_markup=admin_menu_keyboard)


# Изменение ключевых слов
async def change_keywords_model(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_id = data['q_id']
    questions = data['questions']
    keywords = ''

    for quest in questions:
        if q_id == int(quest['id']):
            keywords = quest['keywords']
            break

    await call.message.answer(f'*Текущие ключевые слова:* {keywords}\n'
                              f'*Введите новые ключевые слова (через запятую):*')
    await state.update_data(q_id=q_id, keywords=keywords)
    await state.set_state(StepsQuestionModel.GET_NEW_KEYWORDS)


# Добавление ключевых слов
async def add_keywords_model(message: Message, state: FSMContext):
    data = await state.get_data()
    q_id = data.get('q_id')
    new_keywords = message.text.lower()

    await edit_keywords_api(q_id=q_id, new_keywords=new_keywords)
    await message.answer(f'*Ключевые слова* {new_keywords} добавлены.', reply_markup=admin_menu_keyboard)
    await state.clear()
