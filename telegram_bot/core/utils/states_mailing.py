from aiogram.fsm.state import StatesGroup, State


class StepsMailing(StatesGroup):
    GET_TEXT = State()
    SEND_MESSAGE = State()
