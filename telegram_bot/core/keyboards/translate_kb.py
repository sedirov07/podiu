import pickle
import os
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from ..translate.translator import translate_text


translated_topics_keyboards = {}
translated_questions_keyboards = {}
DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(DIR, '..', '..'))
CACHE_DIR = os.path.join(PROJECT_DIR, 'cache_tg')


async def load_cache():
    global translated_topics_keyboards
    global translated_questions_keyboards
    with open(f"{CACHE_DIR}/translated_topics_keyboards.pkl", "rb") as file:
        translated_topics_keyboards = pickle.load(file)
    with open(f"{CACHE_DIR}/translated_questions_keyboards.pkl", "rb") as file:
        translated_questions_keyboards = pickle.load(file)


async def save_cache():
    with open(f"{CACHE_DIR}/translated_topics_keyboards.pkl", "wb") as file:
        pickle.dump(translated_topics_keyboards, file)
    with open(f"{CACHE_DIR}/translated_questions_keyboards.pkl", "wb") as file:
        pickle.dump(translated_questions_keyboards, file)


async def translate_kb(inline_keyboard, target_language):
    translated_keyboard = []

    for row in inline_keyboard:
        translated_row = []
        for button in row:
            translated_text = await translate_text(button.text, 'en', target_language, cache=True)
            translated_button = InlineKeyboardButton(text=translated_text, callback_data=button.callback_data)
            translated_row.append(translated_button)
        translated_keyboard.append(translated_row)

    return InlineKeyboardMarkup(inline_keyboard=translated_keyboard)


async def translate_reply_kb(reply_keyboard, target_language, buttons):
    translated_keyboard = []

    for row in reply_keyboard.keyboard:
        translated_row = []
        for button in row:
            # Переводим текст кнопки
            translated_text = await translate_text(button.text, 'en', target_language, cache=True)
            if button.text.lower() in buttons:
                if translated_text.lower() not in buttons[button.text.lower()]:
                    buttons[button.text.lower()].append(translated_text.lower())
            # Создаём новую кнопку с переведённым текстом
            translated_button = KeyboardButton(text=translated_text)
            translated_row.append(translated_button)
        translated_keyboard.append(translated_row)

    # Возвращаем новую клавиатуру с переведёнными кнопками
    return ReplyKeyboardMarkup(keyboard=translated_keyboard, resize_keyboard=True, one_time_keyboard=True)


async def translate_faq_keyboard(inline_keyboard, level, target_language):
    if level == 'topic':
        if target_language in translated_topics_keyboards:
            return translated_topics_keyboards[target_language]

        translated_topic_keyboard = await translate_kb(inline_keyboard, target_language)
        translated_topics_keyboards[target_language] = translated_topic_keyboard
        return translated_topic_keyboard

    elif 'question' in level:
        topic = level.split('_')[-1]
        if target_language not in translated_questions_keyboards:
            translated_questions_keyboards[target_language] = {}
        if topic in translated_questions_keyboards[target_language]:
            return translated_questions_keyboards[target_language][topic]

        translated_question_keyboard = await translate_kb(inline_keyboard, target_language)
        translated_questions_keyboards[target_language][topic] = translated_question_keyboard
        return translated_question_keyboard


async def clear_cache(levels):
    if 'topic' == levels:
        translated_topics_keyboards.clear()
    if 'question' == levels:
        translated_questions_keyboards.clear()


async def change_topic_name(old_topic, new_topic):
    for lang, keyboards in translated_questions_keyboards.items():
        if old_topic in keyboards:
            keyboards[new_topic] = keyboards.pop(old_topic)
        else:
            await clear_cache('question')
            break
    await clear_cache('topic')


async def del_topic_name(topic):
    for lang, keyboards in translated_questions_keyboards.items():
        if topic in keyboards:
            del translated_questions_keyboards[lang][topic]
        await clear_cache('topic')
