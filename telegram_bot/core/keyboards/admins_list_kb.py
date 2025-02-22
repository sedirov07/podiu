from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def create_admins_list_kb(admins):
    admins_list_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'{v}',
                callback_data=f'delete_admin_{k}'
            )
        ] for k, v in admins.items()
    ])
    return admins_list_keyboard
