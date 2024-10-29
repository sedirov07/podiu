from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


admin_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Просмотр FAQ'
        ),
        KeyboardButton(
            text='Редактирование FAQ'
        ),
        KeyboardButton(
            text='Модель ответов'
        )
    ],
    [
        KeyboardButton(
            text='Список заявлений'
        ),
        KeyboardButton(
            text='Управление персоналом'
        ),
        KeyboardButton(
            text='Общая рассылка'
        )
    ]
], resize_keyboard=True, one_time_keyboard=True)
