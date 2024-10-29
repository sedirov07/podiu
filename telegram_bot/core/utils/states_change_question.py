from aiogram.fsm.state import StatesGroup, State


class StepsAddQuestion(StatesGroup):
    GET_TOPIC = State()
    GET_QUESTION = State()
    GET_ANSWER = State()


class StepsChangeQuestion(StatesGroup):
    GET_TOPIC = State()
    GET_QUESTION = State()
    GET_ACTION = State()
    GET_NEW_QUESTION = State()
    GET_NEW_ANSWER = State()
