from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


consent_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text="✅ I agree"
        ),
        KeyboardButton(
            text="❌ I don't agree"
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)

for_whom_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text="For myself"
        ),
        KeyboardButton(
            text="For another person"
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)

no_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text="❌ No"
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)

yes_or_no_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text="✅ Yes"
        ),
        KeyboardButton(
            text="❌ No"
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)
