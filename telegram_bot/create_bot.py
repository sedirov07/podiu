import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


BOT_TOKEN = os.getenv('BOT_TOKEN')


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode='MARKDOWN')
dp = Dispatcher(storage=storage)
