from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='FAQ'
        ),
        KeyboardButton(
            text='Apply'
        )
    ],
    [
        KeyboardButton(
            text='Change language'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)
