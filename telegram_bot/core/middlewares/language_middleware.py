from logging_config import conf_logging
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Dict, Any, Callable, Awaitable
from ..translate.translator import detect_language


conf_logging()


class LanguageMiddleware(BaseMiddleware):
    def __init__(self, db, max_cache_size=1000):
        self.db = db
        self.max_cache_size = max_cache_size
        self.user_languages = {}

    async def change_language(self, user_id, lang):
        self.user_languages[user_id] = lang
        await self.db.add_user(user_id, lang)

    async def add_language(self, user_id, lang):
        self.user_languages[user_id] = lang
        await self.db.add_user(user_id, lang)

    async def get_users_languages(self):
        return await self.db.get_users_languages()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        if user_id in self.user_languages:
            user_language = self.user_languages[user_id]
        else:
            user_language = await self.db.get_user_language(user_id)
            if user_language:
                self.user_languages[user_id] = user_language
                if len(self.user_languages) > self.max_cache_size:
                    oldest_user_id = next(iter(self.user_languages))
                    del self.user_languages[oldest_user_id]

        if event.text and not event.text.startswith('/'):
            if not user_language:
                user_language = detect_language(event.text)
                await self.db.add_user(user_id, user_language)
                self.user_languages[user_id] = user_language
                logging.info(f"Added user {user_id} with language {user_language}")
            else:
                logging.info(f"User {user_id} already exists with language {user_language}")

        data['user_language'] = user_language if user_language else None

        return await handler(event, data)
