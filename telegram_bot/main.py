import asyncio
from core.config import setup_environment

# Настройка окружения
setup_environment()

from core.utils.commands import set_commands
from core.utils.dp_register import dp_register
from create_bot import dp, bot
from logging_config import conf_logging


async def start():
    conf_logging()

    # Настройка бота
    await dp_register(dp)
    await set_commands(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
