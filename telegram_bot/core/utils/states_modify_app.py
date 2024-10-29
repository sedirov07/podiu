from aiogram.fsm.state import StatesGroup, State


class StepsModifyApp(StatesGroup):
    GET_NEW_VALUE = State()
    GET_ANOTHER_NEW_VALUE = State()
