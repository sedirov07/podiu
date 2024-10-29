from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsOperator(BaseFilter):
    operators_id = []

    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        try:
            return message.from_user.id in self.operators_id
        except:
            return False

    @classmethod
    def add_operator(cls, operator_id):
        cls.operators_id.append(operator_id)

    @classmethod
    def delete_operator(cls, operator_id):
        for i in range(len(cls.operators_id)):
            if cls.operators_id[i] == operator_id:
                cls.operators_id.pop(i)
