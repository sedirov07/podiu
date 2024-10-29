from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.keyboards.admin_change_faq_kb import (admin_change_faq_keyboard, admin_actions_topics_keyboard,
                                                admin_actions_questions_keyboard)
from core.utils.states_change_topic import StepsAddTopic, StepsChangeTopic
from core.utils.states_change_question import StepsAddQuestion, StepsChangeQuestion
from core.utils.hash_faq import find_question_by_hash
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
    await call.message.edit_text('Выберите вопрос для редактирования: ', reply_markup=questions_keyboard[topic])
    await state.set_state(StepsChangeQuestion.GET_QUESTION)


async def get_question_to_change(call: CallbackQuery, faq_dict, state: FSMContext):
    data = await state.get_data()
    topic = data['topic']
    call_data = call.data.split('_')
    question_hash = call_data[-1]
    question = find_question_by_hash(faq_dict, topic, question_hash)
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
