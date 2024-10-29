from aiogram.fsm.state import StatesGroup, State


class StepsApproveApp(StatesGroup):
    GET_APPROVE = State()
    GET_REASON = State()
