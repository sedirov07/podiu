from aiogram.fsm.state import StatesGroup, State


class StepsAddOperator(StatesGroup):
    GET_OPERATOR = State()
    GET_LAST_NAME = State()
