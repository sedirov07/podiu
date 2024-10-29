from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_change_faq_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Редактирование тем',
            callback_data='change_topics'
        )
    ],
[
        InlineKeyboardButton(
            text='Добавление тем',
            callback_data='add_topics'
        )
    ],
    [
        InlineKeyboardButton(
            text='Редактирование вопросов и ответов',
            callback_data='change_questions_and_answers'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавление вопросов и ответов',
            callback_data='add_questions_and_answers'
        )
    ]
])

admin_actions_topics_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Изменить тему',
            callback_data='change_topic'
        )
    ],
    [
        InlineKeyboardButton(
            text='Удалить тему',
            callback_data='delete_topic'
        )
    ]
])

admin_actions_questions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Изменить вопрос',
            callback_data='change_question'
        )
    ],
    [
        InlineKeyboardButton(
            text='Изменить ответ',
            callback_data='change_answer'
        )
    ],
    [
        InlineKeyboardButton(
            text='Изменить вопрос и ответ',
            callback_data='change_both'
        )
    ],
    [
        InlineKeyboardButton(
            text='Удалить вопрос',
            callback_data='delete_question'
        )
    ]
])
