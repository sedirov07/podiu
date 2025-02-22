from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..keyboards.translate_kb import translate_reply_kb


async def create_menu_keyboard(lang, buttons):
    menu_keyboard = await translate_reply_kb(ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text='FAQ'
            ),
            # KeyboardButton(
            #     text='Apply'
            # ),
            KeyboardButton(
                text='Contacts'
            )
        ],
        [
            KeyboardButton(
                text='Change language'
            )
        ]
    ], resize_keyboard=True, one_time_keyboard=True), lang, buttons)

    return menu_keyboard

# menu_keyboard = ReplyKeyboardMarkup(keyboard=[
#     [
#         KeyboardButton(
#             text='FAQ'
#         ),
#         # KeyboardButton(
#         #     text='Apply'
#         # ),
#         KeyboardButton(
#             text='Contacts'
#         )
#     ],
#     [
#         KeyboardButton(
#             text='Change language'
#         )
#     ]
# ], resize_keyboard=True, one_time_keyboard=True)
