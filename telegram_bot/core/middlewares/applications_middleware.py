import logging
from logging_config import conf_logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Dict, Any, Callable, Awaitable
from core.keyboards.admin_review_kb import review_button


conf_logging()

MAX_APPLICATIONS_IN_KEYBOARD = 10  # Максимальное количество заявлений в клавиатуре


class ApplicationsMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db
        self.applications = []
        self.applications_texts = {}
        self.applications_keyboard_builder = InlineKeyboardBuilder()
        self.applications_keyboard = self.applications_keyboard_builder.as_markup()

    async def load_applications(self):
        try:
            applications = await self.db.get_applications_awaiting_review()
            if len(applications):
                for app in applications:
                    telegram_id = app['telegram_id']
                    last_name = app['last_name']
                    first_name = app['first_name']
                    user_lang = await self.db.get_user_language(telegram_id)
                    await self.add_application(telegram_id, user_lang, last_name, first_name)
        except Exception as e:
            logging.warning(f"An error occurred while loading applications: {e}")

    async def add_application(self, user_id, user_lang, last_name, first_name):
        self.applications.append({
            'telegram_id': user_id,
            'last_name': last_name,
            'first_name': first_name,
            'user_lang': user_lang
        })
        await self.add_application_in_kb(user_id, user_lang, last_name, first_name)

    async def add_application_in_kb(self, user_id, user_lang, last_name, first_name):
        if len(self.applications_keyboard.inline_keyboard) <= MAX_APPLICATIONS_IN_KEYBOARD:
            button = await review_button(user_id, user_lang, last_name, first_name)
            self.applications_keyboard_builder.row(button)
            self.applications_keyboard = self.applications_keyboard_builder.as_markup()

    async def add_application_to_db(self, data):
        return await self.db.add_application(data)

    async def del_application(self, user_id):
        index = await self.is_application(user_id)
        if index is not None:
            self.applications.pop(index)
            self.applications_keyboard_builder = InlineKeyboardBuilder()
            for application in self.applications:
                button = await review_button(application['user_id'], application['user_lang'],
                                             application['last_name'], application['first_name'])
                self.applications_keyboard_builder.row(button)
                self.applications_keyboard = self.applications_keyboard_builder.as_markup()
        if len(self.applications) > 0:
            next_application = self.applications[0]
            await self.add_application_in_kb(next_application['user_id'], next_application['user_lang'],
                                             next_application['last_name'], next_application['first_name'])
        await self.db.delete_application(user_id)

    async def is_application(self, user_id):
        for i in range(len(self.applications)):
            if self.applications[i]['telegram_id'] == int(user_id):
                return i
        return None

    async def add_application_text(self, user_id, app_dict):
        if user_id not in self.applications_texts:
            self.applications_texts[user_id] = {}

        for key, value in app_dict.items():
            self.applications_texts[user_id][key] = value

    async def remove_application_text(self, user_id):
        if self.applications_texts[user_id]:
            del self.applications_texts[user_id]

    async def get_applications(self, user_id):
        return await self.db.get_application(user_id)

    async def update_status(self, user_id, status):
        await self.db.update_status(user_id, status)

    async def update_columns_by_dict(self, old_value_dict, user_id):
        await self.db.update_columns_by_dict(old_value_dict, user_id)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        data['applications'] = self.applications
        data['applications_kb'] = self.applications_keyboard
        data['applications_texts'] = self.applications_texts

        return await handler(event, data)
