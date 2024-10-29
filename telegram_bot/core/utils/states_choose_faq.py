from aiogram.fsm.state import StatesGroup, State


class StepsChooseFaq(StatesGroup):
    GET_TOPIC = State()
    GET_QUESTION = State()
    GET_ANSWER = State()
    CHATTING_CLIENT = State()
    NO_ANSWER_IN_FAQ = State()
