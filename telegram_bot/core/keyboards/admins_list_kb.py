from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def create_admins_list_kb(admins_list):
    admins_list_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'{admin["user_name"]}',
                callback_data=f'delete_admin_{admin["user_id"]}'
            )
        ] for admin in admins_list
    ])
    return admins_list_keyboard
