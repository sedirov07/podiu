from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


app_status_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text="approved"
        ),
        KeyboardButton(
            text="awaiting review"
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)
