from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):
    def __init__(self, admins_id=[]):
        self.admins_id = admins_id

    async def __call__(self, message: Message) -> bool:
        try:
            return message.from_user.id in self.admins_id
        except Exception:
            return False

    async def add_admin(self, admin_id):
        self.admins_id.append(admin_id)

    async def delete_admin(self, admin_id):
        for i in range(len(self.admins_id)):
            if self.admins_id[i] == admin_id:
                self.admins_id.pop(i)
