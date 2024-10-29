import os
import aiohttp
from datetime import datetime, timedelta, timezone
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.keyboards.menu_kb import menu_keyboard
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.translate.translator import translate_text, detect_language, translate_text_with_markdown_links
from core.utils.states_change_lang import StepsChangeLang
from core.utils.states_choose_faq import StepsChooseFaq
from core.utils.hash_faq import find_question_by_hash
from core.middlewares.language_middleware import LanguageMiddleware
from core.middlewares.admins_middleware import AdminsMiddleware
from core.keyboards.translate_kb import translate_faq_keyboard
from core.keyboards.operator_chat_kb import operator_ready_kb
from core.keyboards.faq_kb import contact_with_operator_keyboard


API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")


# Функция для отправки текста на сервер API и получения ответа в виде строки
async def send_text_to_api(text) -> str:
    api = f"http://{API_HOST}:{API_PORT}/answer"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api, json={"question": text}) as response:
                if response.status == 200:
                    response_text = await response.text()
                    response_text = response_text.replace('"', '')
                    if response_text:
                        return response_text
                    return ''
                else:
                    print(f"Error: {response.status}")
                    return text
        except aiohttp.ClientError as e:
            print(f"Error: {e}")
            return text
        except Exception as e:
            print(f"Error: {e}")
            return text


async def get_cancel(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.clear()


async def get_start(message: Message, user_language, state: FSMContext, language_middleware: LanguageMiddleware):
    if await state.get_state() is not None:
        await state.clear()
    user = message.from_user
    lang = user_language or user.language_code
    if not user_language:
        await language_middleware.add_language(user.id, lang)
    await message.answer(translate_text('Hello! To communicate with the bot, You can use the most preferred'
                                        'language for You!', 'en', f'{lang}'), reply_markup=menu_keyboard)


async def change_lang(message: Message, state: FSMContext, user_language):
    await message.answer(translate_text(f'Your language is: "{user_language}"\n'
                                        f'To change: write something in your language', 'en',
                                        user_language))
    await state.set_state(StepsChangeLang.GET_LANG)


async def get_lang(message: Message, state: FSMContext, language_middleware: LanguageMiddleware):
    lang = detect_language(message.text)
    await message.answer(translate_text(f'Your language has been changed to "{lang}"', 'en', f'{lang}'),
                         reply_markup=menu_keyboard)
    await language_middleware.change_language(message.from_user.id, lang)
    await state.clear()


async def get_topics_faq(message: Message, state: FSMContext, topics_keyboard, user_language):
    keyboard = await translate_faq_keyboard(topics_keyboard.inline_keyboard, 'topic', user_language)
    await message.answer(translate_text("Choose a topic:", 'en', user_language), reply_markup=keyboard)
    chat_id = message.from_user.id
    await state.update_data(user_id=chat_id, user_language=user_language)
    await state.set_state(StepsChooseFaq.GET_TOPIC)


async def get_questions_faq(call: CallbackQuery, state: FSMContext, questions_keyboard):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    topic = call.data.split('_')[-1]
    keyboard = await translate_faq_keyboard(questions_keyboard[topic].inline_keyboard, f'question_{topic}',
                                            user_language)
    await call.message.edit_text(translate_text("Choose a question:", 'en', user_language),
                                 reply_markup=keyboard)
    await state.update_data(topic=topic)
    await state.set_state(StepsChooseFaq.GET_QUESTION)


async def get_answer(message: Message, state: FSMContext, user_language):
    question = translate_text(message.text, user_language, 'en')
    answer = await send_text_to_api(question)
    if len(answer) == 0:
        answer = "The bot could not answer your question correctly!"

    await message.answer(translate_text_with_markdown_links(f'Answer from bot:\n{answer}\n'
                                                            f'If you are not satisfied with the answer from the bot,'
                                                            f'you can contact with the operator', 'en', user_language),
                         reply_markup=contact_with_operator_keyboard)
    await state.clear()


async def send_answer_faq(call: CallbackQuery, bot: Bot, state: FSMContext, faq_dict, admins_list, operators,
                          admins_middleware: AdminsMiddleware):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    topic = data.get('topic', 'VISA')
    call_data = call.data.split('_')
    user_id = data.get('user_id')

    if call_data == ['contact', 'with', 'operator']:
        # Создание объекта timezone для UTC+5
        utc_plus_5 = timezone(timedelta(hours=5))

        # Получение текущего времени для UTC+5
        current_time_ekb = datetime.now(utc_plus_5).time()

        if datetime.strptime('08:00', '%H:%M').time() <= current_time_ekb <= datetime.strptime('18:00', '%H:%M').time():
            first_name = call.from_user.first_name
            await state.update_data(first_name=first_name)
            await call.message.edit_text(translate_text("We are looking for a free operator. Wait for it...", 'en',
                                                        user_language))
            await contact_with_operator(bot, operators, first_name, user_id, admins_middleware, user_language)
        else:
            await call.message.answer(translate_text("You can contact the operator only from 3:00 to 13:00 UTC",
                                                     'en', user_language),
                                      reply_markup=menu_keyboard)
        await state.clear()
    elif data.get('reason'):
        await state.clear()
    elif call_data == ['send', 'other', 'question']:
        await call.message.answer(translate_text("Write your question:", 'en', user_language))
        await state.set_state(StepsChooseFaq.NO_ANSWER_IN_FAQ)
    else:
        question_hash = call_data[-1]
        question = find_question_by_hash(faq_dict, topic, question_hash)
        await call.message.edit_text(translate_text_with_markdown_links(faq_dict[topic][question], 'en', user_language))
        if 'Where is Ekaterinburg?' == question:
            latitude = 56.838011
            longitude = 60.597474
            await bot.send_location(user_id, latitude, longitude)
        if user_id in [admin['user_id'] for admin in admins_list]:
            await call.message.answer('Меню:', reply_markup=admin_menu_keyboard)
        else:
            await call.message.answer(translate_text('Menu:', 'en', user_language), reply_markup=menu_keyboard)

        await state.clear()


async def contact_with_operator(bot, operators, first_name, user_id, admins_middleware, user_language):
    messages = []
    keyboard = await operator_ready_kb(user_id, user_language, first_name)

    for operator, operator_dict in operators.items():
        message = await bot.send_message(operator, f"С Вами хочет связатья пользователь {first_name}. "
                                                   f"Язык пользователя: {user_language}. Отправить ему Ваш контакт?",
                                         reply_markup=keyboard)
        messages.append({operator: message.message_id})

    await admins_middleware.add_messages(user_id, messages)


async def operator_ready(call: CallbackQuery, bot: Bot, admins_middleware: AdminsMiddleware, messages_dicts, operators):
    operator_id = call.from_user.id
    call_data = call.data.split('_')
    user_id = int(call_data[-3])
    user_language = call_data[-2]
    first_name_client = call_data[-1]

    await send_contact(bot, operators, operator_id, user_id, user_language)
    await bot.send_message(operator_id, f"Ваш контакт был перенаправлен пользователю {first_name_client}")
    for message in messages_dicts[user_id]:
        for key, value in message.items():
            operator_id = key
            message_id = value
            await bot.edit_message_reply_markup(operator_id, message_id, reply_markup=None)
        break
    await admins_middleware.del_messages(user_id)


async def operator_not_ready(call: CallbackQuery):
    await call.message.edit_text('Вы отклонили приглашение в чат.', reply_markup=None)


async def send_contact(bot, operators, operator_id, user_id, user_language):
    operator = operators[operator_id]
    operator_full_name = operator['first_name'] + ' ' + operator['last_name']
    operator_contact = operator['contact']
    phone = operator_contact.phone_number
    first_name = operator_contact.first_name
    await bot.send_message(user_id, translate_text(f'The operator is contact {operator_full_name} has been sent to you'
                                                   f'to discuss your questions:', 'en', user_language))
    await bot.send_contact(user_id, phone_number=phone, first_name=first_name)
