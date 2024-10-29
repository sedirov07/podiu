from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):
    admins_id = []

    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        try:
            return message.from_user.id in self.admins_id
        except:
            return False

    @classmethod
    def add_admin(cls, admin_id):
        cls.admins_id.append(admin_id)

    @classmethod
    def delete_admin(cls, admin_id):
        for i in range(len(cls.admins_id)):
            if cls.admins_id[i] == admin_id:
                cls.admins_id.pop(i)
