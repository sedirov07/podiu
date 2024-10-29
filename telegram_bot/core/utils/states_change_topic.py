from aiogram.fsm.state import StatesGroup, State


class StepsAddTopic(StatesGroup):
    GET_TOPIC = State()


class StepsChangeTopic(StatesGroup):
    GET_TOPIC = State()
    GET_ACTION = State()
    GET_NEW_TOPIC = State()
