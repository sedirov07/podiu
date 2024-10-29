import logging
from logging_config import conf_logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Dict, Any, Callable, Awaitable


conf_logging()


class AdminsMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db
        self.operators = {}
        self.messages_to_operators = {}
        self.admins_list = None

    async def load_admins_list(self):
        try:
            self.admins_list = await self.db.get_full_admins_info()
        except Exception as e:
            logging.error(f"An error occurred while loading admins list: {e}")

    async def add_operator(self, chat_id, first_name, last_name, contact):
        self.operators[chat_id] = {
            'first_name': first_name,
            'last_name': last_name,
            'contact': contact
        }

    async def del_operator(self, chat_id):
        if chat_id in self.operators:
            del self.operators[chat_id]

    async def add_admin(self, chat_id, full_name):
        self.admins_list.append((chat_id, full_name))
        await self.db.add_admin(chat_id, full_name)

    async def del_admin(self, chat_id):
        for admin in self.admins_list:
            if admin['user_id'] == chat_id:
                self.admins_list.remove(admin['user_id'])
        await self.db.delete_admin(chat_id)

    async def add_messages(self, user_id, messages):
        self.messages_to_operators[user_id] = messages

    async def del_messages(self, user_id):
        if user_id in self.messages_to_operators:
            del self.messages_to_operators[user_id]

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if self.admins_list is None:
            await self.load_admins_list()

        if self.admins_list:
            data['admins_list'] = self.admins_list

        data['operators'] = self.operators
        data['messages_dicts'] = self.messages_to_operators

        return await handler(event, data)
