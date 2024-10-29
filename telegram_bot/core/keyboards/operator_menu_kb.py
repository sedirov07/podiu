from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


operator_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Просмотр FAQ'
        ),
        KeyboardButton(
            text='Список заявлений'
        ),
        KeyboardButton(
            text='Редактирование FAQ'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)
