from core.utils.hash_faq import hash_string
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Создание клавиатуры для списка тем
async def create_topic_keyboard(faq_dict):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=topic,
                callback_data=f'topic_{topic}'
            )
        ] for topic, questions in faq_dict.items()
    ])

    return keyboard


# Создание клавиатуры для списка вопросов
async def create_question_keyboard(faq_dict):
    keyboards = {}
    for topic, questions in faq_dict.items():
        keyboard_buttons = [
            [
                InlineKeyboardButton(
                    text=question,
                    callback_data=f'qu_{hash_string(question)}'
                )
            ] for question, answer in questions.items()
        ]

        keyboard_buttons.append([
            InlineKeyboardButton(
                text='Contact with operator',
                callback_data='contact_with_operator'
            )]
        )

        keyboard_buttons.append([
            InlineKeyboardButton(
                text='Send other question',
                callback_data='send_other_question'
            )]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        keyboards[topic] = keyboard
    return keyboards


contact_with_operator_keyboard = InlineKeyboardMarkup(inline_keyboard=
    [
        [
            InlineKeyboardButton(
                text='Contact with operator',
                callback_data='contact_with_operator'
            )
        ]
    ]
)
