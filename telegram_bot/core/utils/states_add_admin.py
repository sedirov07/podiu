from aiogram.fsm.state import StatesGroup, State


class StepsAddAdmin(StatesGroup):
    GET_ADMIN = State()
