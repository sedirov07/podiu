from aiogram.fsm.state import StatesGroup, State


class StepsChangeLang(StatesGroup):
    GET_LANG = State()
