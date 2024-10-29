from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def create_apply_keyboard(text, user_id, user_lang):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'{key}: {value}',
                callback_data=f'mod_app_{key}_{user_id}_{user_lang}'
            )
        ] for key, value in text.items()
    ])

    return keyboard
