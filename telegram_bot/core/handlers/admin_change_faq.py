import os
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.keyboards.admin_change_faq_kb import (admin_change_faq_keyboard, admin_actions_topics_keyboard,
                                                admin_actions_questions_keyboard, create_paginated_keyboard,
                                                create_paginated_keyboard_docs)
from core.utils.states_change_topic import StepsAddTopic, StepsChangeTopic
from core.utils.states_change_question import StepsAddQuestion, StepsChangeQuestion
from core.utils.states_change_documents import StepsAddDocument
from core.utils.hash_faq import find_question_by_hash
from core.utils.change_dir import delete_doc_file, DOCS_DIR
from core.middlewares.faq_middleware import FAQMiddleware
from core.keyboards.translate_kb import clear_cache, change_topic_name, del_topic_name
from core.translate.translator import del_translation_text


async def get_start(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.clear()
    await message.answer('Вы авторизованы как администратор.', reply_markup=admin_menu_keyboard)


async def change_faq(message: Message):
    await message.answer('Выберите: ', reply_markup=admin_change_faq_keyboard)


async def start_add_topic(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Введите новую тему.')
    await state.set_state(StepsAddTopic.GET_TOPIC)


async def finish_add_topic(message: Message, state: FSMContext, faq_middleware: FAQMiddleware):
    topic = message.text
    await faq_middleware.add_topic(topic)
    await clear_cache('topic')
    await faq_middleware.load_faq_dict()
    await message.answer('Тема была успешно добавлена!', reply_markup=admin_menu_keyboard)
    await state.clear()


async def start_change_topic(call: CallbackQuery, topics_keyboard, state: FSMContext):
    await call.message.edit_text('Выберите заголовок для редактирования: ', reply_markup=topics_keyboard)
    await state.set_state(StepsChangeTopic.GET_TOPIC)


async def get_topic_to_change(call: CallbackQuery, state: FSMContext):
    topic = call.data.split('_')[-1]
    await state.update_data(topic=topic)
    await call.message.edit_text('Выберите действие: ', reply_markup=admin_actions_topics_keyboard)
    await state.set_state(StepsChangeTopic.GET_ACTION)


async def change_topic(call: CallbackQuery, state: FSMContext, faq_middleware: FAQMiddleware):
    data = await state.get_data()
    topic = data['topic']
    action = call.data
    if action == 'delete_topic':
        topic_delete = await faq_middleware.delete_topic(topic)

        if topic_delete:
            await del_topic_name(topic)
            await faq_middleware.load_faq_dict()
            await del_translation_text(topic)
            await call.message.answer('Тема была успешно удалена!', reply_markup=admin_menu_keyboard)
        else:
            await call.message.answer('Тема не может быть удалена, так как в ней находятся вопросы, сначала '
                                      'удалите все вопросы в этой теме!', reply_markup=admin_menu_keyboard)
        await state.clear()
    elif action == 'change_topic':
        await call.message.edit_text('Введите новое название для темы:')
        await state.set_state(StepsChangeTopic.GET_NEW_TOPIC)


async def rename_topic(message: Message, state: FSMContext, faq_middleware: FAQMiddleware):
    data = await state.get_data()
    old_topic = data['topic']
    new_topic = message.text
    await faq_middleware.change_topic(old_topic, new_topic)
    await change_topic_name(old_topic, new_topic)
    await faq_middleware.load_faq_dict()
    await del_translation_text(old_topic)
    await message.answer('Тема была успешно изменена!', reply_markup=admin_menu_keyboard)
    await state.clear()


async def start_add_question(call: CallbackQuery, topics_keyboard, state: FSMContext):
    await call.message.edit_text('Выберите заголовок в котором хотите добавить новый вопрос.',
                                 reply_markup=topics_keyboard)
    await state.set_state(StepsAddQuestion.GET_TOPIC)


async def get_topic_of_question_to_add(call: CallbackQuery, state: FSMContext):
    topic = call.data.split('_')[-1]
    await state.update_data(topic=topic)
    await call.message.edit_text('Введите текст вопроса')
    await state.set_state(StepsAddQuestion.GET_QUESTION)


async def get_question_to_add(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer('Введите текст ответа на вопрос, учитывая следующие стили оформления: \n'
                         '\\**Жирный текст*\\*, \\__Курсив_\\_ \n'
                         '\\[гиперссылка](ссылка) ')
    await state.set_state(StepsAddQuestion.GET_ANSWER)


async def finish_add_question(message: Message, state: FSMContext, faq_middleware: FAQMiddleware):
    data = await state.get_data()
    answer = message.text
    topic = data['topic']
    question = data['question']
    await faq_middleware.add_question_answer(topic, question, answer)
    await clear_cache('question')
    await faq_middleware.load_faq_dict()
    await message.answer('Вопрос был успешно добавлен!', reply_markup=admin_menu_keyboard)
    await state.clear()


async def start_change_question(call: CallbackQuery, topics_keyboard, state: FSMContext):
    await call.message.edit_text('Выберите заголовок в котором находится вопрос для редактирования: ',
                                 reply_markup=topics_keyboard)
    await state.set_state(StepsChangeQuestion.GET_TOPIC)


async def get_topic_of_question_to_change(call: CallbackQuery, questions_keyboard, state: FSMContext):
    topic = call.data.split('_')[-1]
    await state.update_data(topic=topic)
    kb = questions_keyboard[topic].copy()
    kb.inline_keyboard = kb.inline_keyboard[:-2]
    await call.message.edit_text('Выберите вопрос для редактирования: ', reply_markup=kb)
    await state.set_state(StepsChangeQuestion.GET_QUESTION)


async def get_question_to_change(call: CallbackQuery, faq_dict, state: FSMContext):
    data = await state.get_data()
    topic = data['topic']
    call_data = call.data.split('_')
    question_hash = call_data[-1]
    question = await find_question_by_hash(faq_dict, topic, question_hash)
    answer = faq_dict[topic][question]
    await state.update_data(question=question, answer=answer, new_question=question, new_answer=answer)
    await call.message.edit_text('Выберите действие: ', reply_markup=admin_actions_questions_keyboard)
    await state.set_state(StepsChangeQuestion.GET_ACTION)


async def change_question(call: CallbackQuery, state: FSMContext, faq_middleware: FAQMiddleware):
    action = call.data
    await state.update_data(action=action)
    if action == 'delete_question':
        data = await state.get_data()
        question = data['question']
        await faq_middleware.delete_question(question)
        await clear_cache('question')
        await faq_middleware.load_faq_dict()
        await del_translation_text(question)
        await call.message.answer('Вопрос был успешно удален!', reply_markup=admin_menu_keyboard)
        await state.clear()
    elif action == 'change_question':
        await call.message.edit_text('Введите новый вопрос: ')
        await state.set_state(StepsChangeQuestion.GET_NEW_QUESTION)
    elif action == 'change_answer':
        await call.message.edit_text('Введите новый ответ, учитывая следующие стили оформления: \n'
                                     '\\**Жирный текст*\\*, \\__Курсив_\\_ \n'
                                     '\\[гиперссылка](ссылка) ')
        await state.set_state(StepsChangeQuestion.GET_NEW_ANSWER)
    elif action == 'change_both':
        await call.message.edit_text('Введите новый вопрос: ')
        await state.set_state(StepsChangeQuestion.GET_NEW_QUESTION)


async def rename_question(message: Message, state: FSMContext, faq_middleware: FAQMiddleware):
    question = message.text
    await state.update_data(new_question=question)
    data = await state.get_data()
    if data['action'] == 'change_question':
        await finish_change_question(message, state, faq_middleware)
    elif data['action'] == 'change_both':
        await message.answer('Введите новый ответ, учитывая следующие стили оформления: \n'
                             '\\**Жирный текст*\\*, \\__Курсив_\\_ \n'
                             '\\[гиперссылка](ссылка) ')
        await state.set_state(StepsChangeQuestion.GET_NEW_ANSWER)


async def rename_answer(message: Message, state: FSMContext, faq_middleware: FAQMiddleware):
    answer = message.text
    await state.update_data(new_answer=answer)
    await finish_change_question(message, state, faq_middleware)


# Not a handler
async def finish_change_question(message, state, faq_middleware):
    data = await state.get_data()
    answer = data.get('answer')
    topic = data['topic']
    question = data['question']
    new_question = data['new_question']
    new_answer = data['new_answer']
    await faq_middleware.change_question(topic, question, new_question, new_answer)
    await clear_cache('question')
    await faq_middleware.load_faq_dict()
    await del_translation_text(question)
    await del_translation_text(answer)
    await message.answer('Вопрос был успешно изменен!', reply_markup=admin_menu_keyboard)
    await state.clear()


async def start_delete_document(call: CallbackQuery, questions_and_paths, page: int = 1):
    questions_and_paths_ = [q for q in questions_and_paths if q[-1][0] is not None]
    questions_kb = await create_paginated_keyboard(questions_and_paths_, page)

    await call.message.edit_text('Выберите вопрос в котором находятся документы для удаления: ',
                                 reply_markup=questions_kb)


async def choose_document(call: CallbackQuery, questions_and_paths, page: int = 1):
    qa_id = int(call.data.split('_')[-1])
    documents_ids = []
    documents_names = []
    # documents_paths = []
    for q in questions_and_paths:
        if q[0] == qa_id:
            # documents_paths = q[-1]
            documents_names = q[-2]
            documents_ids = q[-3]
            break
    documents_kb = await create_paginated_keyboard_docs(qa_id, documents_ids, documents_names, page)
    await call.message.edit_text('Выберите документ для удаления: ', reply_markup=documents_kb)


async def delete_document(call: CallbackQuery, questions_and_paths, faq_middleware: FAQMiddleware):
    doc_id = int(call.data.split('_')[-1])
    document_path = ''
    document_name = ''
    for q in questions_and_paths:
        if doc_id in q[-3]:
            ind = q[-3].index(doc_id)
            document_path = q[-1][ind]
            document_name = q[-2][ind]
            break

    await faq_middleware.del_document(doc_id)
    await delete_doc_file(document_path)
    await faq_middleware.load_faq_dict()
    await call.message.answer(f'Документ {document_name} был успешно удален!', parse_mode='HTML',
                              reply_markup=admin_menu_keyboard)


async def start_add_document(call: CallbackQuery, topics_keyboard, state: FSMContext):
    await call.message.edit_text('Выберите заголовок в котором хотите добавить новый документ.',
                                 reply_markup=topics_keyboard)
    await state.set_state(StepsAddDocument.GET_TOPIC)


async def get_topic_of_question_to_add_document(call: CallbackQuery, questions_keyboard, state: FSMContext):
    topic = call.data.split('_')[-1]
    await state.update_data(topic=topic)
    kb = questions_keyboard[topic].copy()
    kb.inline_keyboard = kb.inline_keyboard[:-2]
    await call.message.edit_text('Выберите вопрос для добавления документа: ', reply_markup=kb)
    await state.set_state(StepsAddDocument.GET_QUESTION)


async def get_question_to_add_document(call: CallbackQuery, faq_dict, state: FSMContext):
    data = await state.get_data()
    topic = data['topic']
    call_data = call.data.split('_')
    question_hash = call_data[-1]
    question = await find_question_by_hash(faq_dict, topic, question_hash)
    answer = faq_dict[topic][question]
    await state.update_data(question=question, answer=answer)
    await call.message.edit_text('Отправьте документ для добавления к ответу.')
    await state.set_state(StepsAddDocument.GET_DOCUMENT)


async def get_document_to_add(message: Message, bot: Bot, faq_middleware: FAQMiddleware, state: FSMContext):
    # Получаем информацию о документе
    data = await state.get_data()
    document = message.document
    file_id = document.file_id
    file_name = document.file_name
    file_size = document.file_size
    save_path = os.path.join(DOCS_DIR, file_name)
    max_file_size = 20 * 1024 * 1024  # 20 МБ

    if os.path.exists(save_path):
        await message.answer("Файл с таким названием уже существует.")
        return

    if file_size > max_file_size:
        await message.answer("Файл слишком большой. Максимальный размер: 20 МБ.")
        return

    print(
        f"Документ получен:\n"
        f"Имя файла: {file_name}\n"
        f"Размер файла: {file_size} байт"
    )

    # Скачиваем файл
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Сохраняем файл на локальный диск
    await bot.download_file(file_path, save_path)
    print(f"Файл сохранен: {save_path}")

    question = data['question']
    await faq_middleware.add_document(question, file_name, save_path)
    await faq_middleware.load_faq_dict()
    file_name = '.'.join(file_name.split(".")[:-1])#.replace("_", " ")
    await message.answer(f'Документ {file_name} был успешно добавлен!', parse_mode='HTML',
                         reply_markup=admin_menu_keyboard)
    await state.clear()


async def handle_pagination_faq(call: CallbackQuery, questions_and_paths):
    data = call.data
    if data.startswith('qa_doc_page_'):
        page = int(data.split('_')[-1])
        questions_and_paths_ = [q for q in questions_and_paths if q[-1][0] is not None]
        questions_kb = await create_paginated_keyboard(questions_and_paths_, page)
        await call.message.edit_reply_markup(reply_markup=questions_kb)
    elif data == 'qa_doc_cancel_action':
        await call.message.delete()


async def handle_pagination_doc(call: CallbackQuery, questions_and_paths):
    data = call.data
    if data.startswith('doc_page_'):
        qa_id = int(data.split('_')[-2])
        page = int(data.split('_')[-1])
        documents_ids = []
        documents_names = []
        for q in questions_and_paths:
            if q[0] == qa_id:
                documents_names = q[-2]
                documents_ids = q[-3]
                break
        documents_kb = await create_paginated_keyboard_docs(documents_ids, documents_names, page)
        await call.message.edit_reply_markup(reply_markup=documents_kb)
    elif data == 'doc_cancel_action':
        await call.message.delete()
