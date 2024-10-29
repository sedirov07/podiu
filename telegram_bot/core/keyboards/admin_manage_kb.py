from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


admin_manage_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Добавить администратора'
        ),
        KeyboardButton(
            text='Удалить администратора'
        ),
    ],
    [
        KeyboardButton(
            text='Добавить оператора'
        ),
        KeyboardButton(
            text='Удалить оператора'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)
