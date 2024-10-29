from aiogram.fsm.state import StatesGroup, State


class StepsQuestionModel(StatesGroup):
    GET_ACTION = State()
    GET_NEW_QUESTION = State()
    GET_NEW_ANSWER = State()
    GET_NEW_QUESTION_ADD = State()
    GET_NEW_ANSWER_ADD = State()
    GET_NEW_KEYWORDS = State()
