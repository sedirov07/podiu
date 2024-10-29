from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.keyboards.operator_menu_kb import operator_menu_keyboard


async def get_start(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.clear()
    await message.answer('Вы авторизованы как оператор.', reply_markup=operator_menu_keyboard)
