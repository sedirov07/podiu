import asyncio
from core.config import setup_environment

# Настройка окружения
setup_environment()

from core.keyboards.translate_kb import save_cache, load_cache
from core.translate.translator import save_cache as save_cache2, load_cache as load_cache2
from core.utils.commands import set_commands
from core.utils.dp_register import dp_register, save_buttons
from create_bot import dp, bot
from logging_config import conf_logging


async def start():
    conf_logging()

    # Настройка бота
    await dp_register(dp)
    await set_commands(bot)

    try:
        await load_cache()
        await load_cache2()
        await dp.start_polling(bot)
    finally:
        await save_buttons()
        await save_cache()
        await save_cache2()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
