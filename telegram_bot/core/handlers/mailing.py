from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.translate.translator import translate_text
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.keyboards.yes_or_no_kb import yes_or_no_keyboard
from core.utils.states_mailing import StepsMailing
from core.middlewares.language_middleware import LanguageMiddleware


async def start_mailing(message: Message, state: FSMContext):
    await message.answer('Введите сообщение для общей рассылки (на русском языке)')
    await state.set_state(StepsMailing.GET_TEXT)


async def get_text_for_mailing(message: Message, state: FSMContext):
    await state.update_data(message=message.text, first_name=message.from_user.first_name)
    await message.answer(f'Вы уверены, что хотите совершить общую рассылку сообщения:\n'
                         f'{message.text}?', reply_markup=yes_or_no_keyboard)
    await state.set_state(StepsMailing.SEND_MESSAGE)


async def finish_mailing(message: Message, bot: Bot, state: FSMContext, language_middleware: LanguageMiddleware):
    if message.text.lower() == 'да':
        data = await state.get_data()
        mail_message = data.get('message')
        first_name = data.get('first_name')

        users_languages = await language_middleware.get_users_languages()
        counter = 0
        for user_id, language in users_languages.items():
            await bot.send_message(user_id, translate_text(f'General mailing of messages from {first_name}:\n'
                                                           f'{mail_message}', 'en', language))
            counter += 1
        await message.answer(f'Рассылка окончена! Количество отправленных сообщений: {counter}')
    else:
        await message.answer('Меню:', reply_markup=admin_menu_keyboard)
    await state.clear()
