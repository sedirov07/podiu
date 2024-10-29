from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def create_operators_list_kb(operators):
    admins_list_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{operator['first_name']} {operator['last_name']}",
                callback_data=f'delete_operator_{operator_id}'
            )
        ] for operator_id, operator in operators.items()
    ])
    return admins_list_keyboard
