import logging
from logging_config import conf_logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Dict, Any, Callable, Awaitable
from core.keyboards.faq_kb import create_topic_keyboard, create_question_keyboard


conf_logging()


class FAQMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db
        self.faq_dict = None
        self.topics_keyboard = None
        self.questions_keyboard = None

    async def load_faq_dict(self):
        try:
            self.faq_dict = await self.db.get_faq_dict()
            self.topics_keyboard = await create_topic_keyboard(self.faq_dict)
            self.questions_keyboard = await create_question_keyboard(self.faq_dict)
        except Exception as e:
            logging.error(f"An error occurred while loading FAQ data: {e}")

    async def add_topic(self, topic):
        await self.db.add_topic(topic)

    async def delete_topic(self, topic):
        return await self.db.delete_topic(topic)

    async def change_topic(self, old_topic, new_topic):
        await self.db.change_topic(old_topic, new_topic)

    async def add_question_answer(self, topic, question, answer):
        await self.db.add_question_answer(topic, question, answer)

    async def delete_question(self, question):
        await self.db.delete_question(question)

    async def change_question(self, topic, question, new_question, new_answer):
        await self.db.change_question(topic, question, new_question, new_answer)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        data['topics_keyboard'] = self.topics_keyboard
        data['questions_keyboard'] = self.questions_keyboard
        data['faq_dict'] = self.faq_dict

        return await handler(event, data)
