from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


async def review_kb(user_id, user_lang, last_name, first_name):
    review_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'Рассмотреть завявление от {last_name} {first_name}',
                callback_data=f'review_application_{user_id}_{user_lang}'
            )
        ]
    ])
    return review_keyboard


async def review_button(user_id, user_lang, last_name, first_name):
    button = InlineKeyboardButton(
        text=f'Рассмотреть завявление от {last_name} {first_name}',
        callback_data=f'review_application_{user_id}_{user_lang}'
    )

    return button


approve_application_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Одобрить заявление'
        ),
        KeyboardButton(
            text='Редактировать заявление'
        ),
        KeyboardButton(
            text='Отклонить заявление'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)
