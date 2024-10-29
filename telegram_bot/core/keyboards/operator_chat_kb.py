from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


admin_finish_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Завершить чат'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)


async def operator_ready_kb(user_id, user_lang, first_name):
    operator_ready_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Готов',
                    callback_data=f'operator_is_ready_{user_id}_{user_lang}_{first_name}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Не готов',
                    callback_data='operator_is_not_ready'
                )
            ]
    ])

    return operator_ready_keyboard
