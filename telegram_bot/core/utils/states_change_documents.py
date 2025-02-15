from aiogram.fsm.state import StatesGroup, State


class StepsAddDocument(StatesGroup):
    GET_TOPIC = State()
    GET_QUESTION = State()
    GET_DOCUMENT = State()
