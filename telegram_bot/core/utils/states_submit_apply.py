from aiogram.fsm.state import StatesGroup, State


class StepsApply(StatesGroup):
    WAITING_FOR_CONSENT = State()
    WAITING_FOR_PERSONAL_INFO = State()
    WAITING_FOR_PASSPORT = State()
    WAITING_FOR_RU_PASSPORT = State()
    WAITING_FOR_VISA = State()
    WAITING_FOR_BANK_STATEMENT = State()
    WAITING_FOR_TYPE = State()
    WAITING_FOR_COMMENTS = State()
    WAITING_FOR_APPLY = State()
