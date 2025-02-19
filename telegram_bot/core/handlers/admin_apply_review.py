from aiogram import Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from core.keyboards.admin_review_kb import approve_application_keyboard
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.keyboards.modify_apply_kb import create_apply_keyboard
from core.keyboards.yes_or_no_kb import yes_or_no_keyboard
from core.keyboards.consent_kb import for_whom_keyboard
from core.keyboards.app_status_kb import app_status_keyboard
from core.utils.states_approve_app import StepsApproveApp
from core.utils.states_modify_app import StepsModifyApp
from core.utils.sanitize import sanitize_text
from core.translate.translator import translate_text
from core.middlewares.applications_middleware import ApplicationsMiddleware


async def review_application(call: CallbackQuery, bot: Bot, state: FSMContext,
                             applications_middleware: ApplicationsMiddleware):
    operator_id = call.from_user.id
    call_data = call.data.split('_')
    user_id = int(call_data[-2])
    user_lang = call_data[-1]
    text, pdf, jpg = await applications_middleware.get_applications(user_id)
    text = {k: await sanitize_text(v) if isinstance(v, str) else v for k, v in text.items()}

    if text or pdf or jpg:
        full_text = '\n'.join([f'*{key}:* {value}' for key, value in text.items()
                               if not key == 'telegram id' and value])
        new_text = text
        del new_text['telegram id']
        await state.update_data(full_text=new_text)
        await call.message.answer(full_text)

        for description, path in jpg.items():
            photo = FSInputFile(path)
            await bot.send_photo(operator_id, photo=photo, caption=f'*{description}*')

        for description, path in pdf.items():
            pdf = FSInputFile(path)
            await bot.send_document(operator_id, document=pdf, caption=f'*{description}*')

        await call.message.answer('Выберите действие:', reply_markup=approve_application_keyboard)
        await state.update_data(user_id=user_id, user_lang=user_lang)
        await state.set_state(StepsApproveApp.GET_APPROVE)
    else:
        await call.message.answer('Произошла ошибка при выводе данных заявления.')


async def approve_application(message: Message, applications_middleware: ApplicationsMiddleware, bot: Bot,
                              state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    user_lang = data['user_lang']
    approve = message.text

    if approve == 'Одобрить заявление':
        # Отправка заявления в CMS БД!!!
        await applications_middleware.del_application(user_id)
        await applications_middleware.update_status(user_id, 'approved')
        await bot.send_message(user_id, await translate_text('Your application has been approved!', 'en', user_lang,
                                                             cache=True))
        await message.answer('Заявление одобрено, заявитель уведомлен!', reply_markup=admin_menu_keyboard)
        await state.clear()
    elif approve == 'Редактировать заявление':
        full_text = data.get('full_text')
        await applications_middleware.add_application_text(user_id, full_text)
        keyboard_text = await create_apply_keyboard(full_text, user_id, user_lang)
        await message.answer('Выберите что Вы хотите изменить: ', reply_markup=keyboard_text)
        await state.clear()
    elif approve == 'Отклонить заявление':
        await message.answer('Укажите причину отказа (на русском языке).')
        await applications_middleware.del_application(user_id)
        await state.set_state(StepsApproveApp.GET_REASON)


async def rejected_application(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    user_lang = data['user_lang']
    reason = message.text
    full_name = message.from_user.full_name
    await message.answer('Заявление было отклонено.')
    await bot.send_message(user_id,
                           await translate_text(f'Ваше заявление было отклонено оператором {full_name} по причине:\n{reason}',
                                                'ru', user_lang))
    await state.clear()


async def get_applications_list(message: Message, applications, applications_kb):
    counter = len(applications)
    if applications and applications_kb:
        await message.answer(f'Количество заявлений - {counter} \n'
                             f'Выберите заявление для рассмотрения: ', reply_markup=applications_kb)
    else:
        await message.answer('Новых заявлений нет.', reply_markup=admin_menu_keyboard)


async def modify_application(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    user_lang = data[-1]
    user_id = int(data[-2])
    field = data[-3].replace(' ', '_')

    if field == 'status':
        await call.message.answer('Выберите:', reply_markup=app_status_keyboard)
    elif field == 'application_for_self':
        await call.message.answer('Выберите:', reply_markup=for_whom_keyboard)
    else:
        await call.message.edit_text(f"Введите новое значение поля *{field.replace('_', ' ')}:*")

    await state.update_data(user_id=user_id, field=field, user_lang=user_lang)
    await state.set_state(StepsModifyApp.GET_NEW_VALUE)


async def update_application(message: Message, state: FSMContext):
    data = await state.get_data()
    new_value = message.text
    user_id = data.get('user_id')
    field = data.get('field')
    if user_id not in data:
        data[user_id] = {}
    data[user_id][field] = new_value
    await state.update_data(data)
    await message.answer('Вы хотите внести изменения в еще одно поле?', reply_markup=yes_or_no_keyboard)
    await state.set_state(StepsModifyApp.GET_ANOTHER_NEW_VALUE)


async def process_update_application(message: Message, bot: Bot, applications_middleware: ApplicationsMiddleware,
                                     applications_texts, state: FSMContext):
    data = await state.get_data()
    user_lang = data.get('user_lang', 'en')
    user_id = data.get('user_id')
    old_value_dict = {}
    for key, value in applications_texts[user_id].items():
        old_value_dict[key] = value
    new_value_dict = data.get(user_id)
    for key, value in new_value_dict.items():
        old_value_dict[key.replace('_', ' ')] = value
    data[user_id] = old_value_dict

    await state.update_data(data)

    if message.text == 'Да':
        keyboard_text = await create_apply_keyboard(old_value_dict, user_id, user_lang)
        await message.answer('Выберите что Вы хотите изменить: ', reply_markup=keyboard_text)

    elif message.text == 'Нет':
        if old_value_dict['status'] == 'approved':
            await applications_middleware.del_application(user_id)
            await bot.send_message(user_id, await translate_text('Your application has been approved!', 'en',
                                                                 user_lang, cache=True))
            await applications_middleware.update_columns_by_dict(old_value_dict, user_id)
            await message.answer('Заявление успешно изменено и одобрено! Заявитель был уведомлен.',
                                 reply_markup=admin_menu_keyboard)
        else:
            await bot.send_message(user_id, await translate_text('Your application has been changed!', 'en',
                                                                 user_lang, cache=True))
            await applications_middleware.update_columns_by_dict(old_value_dict, user_id)
            await message.answer('Заявление успешно изменено!',
                                 reply_markup=admin_menu_keyboard)
        await state.clear()
