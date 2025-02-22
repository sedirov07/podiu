import logging
import re
import phonenumbers
from datetime import datetime, timedelta, timezone
from logging_config import conf_logging
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.keyboards.consent_kb import consent_keyboard, for_whom_keyboard, no_keyboard, yes_or_no_keyboard
from core.keyboards.menu_kb import create_menu_keyboard
from core.keyboards.admin_review_kb import review_kb
from core.keyboards.faq_kb import contact_with_operator_keyboard
from core.middlewares.applications_middleware import ApplicationsMiddleware
from core.translate.translator import translate_text
from core.utils.states_submit_apply import StepsApply
from core.utils.change_dir import make_dir
from core.ocr.yandex_ocr import file_base64_to_text


conf_logging()


async def validate_phone_number(phone_number):
    try:
        # Попытка разобрать введенный номер телефона
        parsed_number = phonenumbers.parse(phone_number, None)

        # Проверка на валидность номера телефона
        is_valid = phonenumbers.is_valid_number(parsed_number)

        return is_valid
    except phonenumbers.phonenumberutil.NumberParseException as e:
        # Обработка исключения, если номер не удалось разобрать
        logging.error(f"Ошибка при разборе номера телефона: {e}")
        return False


async def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(regex, email))


async def start_submit_apply(message: Message, applications_middleware: ApplicationsMiddleware, buttons,
                             user_language, state: FSMContext):
    user_id = message.from_user.id
    is_user = await applications_middleware.is_application(user_id)
    if is_user is None:
        await state.update_data(user_language=user_language)
        # Отправляем сообщение с просьбой о согласии на обработку личных данных
        await message.answer(await translate_text("Do you give your consent to the processing of your personal data, as well "
                                                  "as the consent of the students listed in the list of participants, in "
                                                  "accordance with Federal Law No. 152-FZ dated 07/27/2006 "
                                                  "\"On Personal Data\", on the terms and for the purposes specified in the "
                                                  "Consent to the processing of personal data?", 'en', user_language, cache=True),
                             reply_markup=consent_keyboard)
        await state.set_state(StepsApply.WAITING_FOR_CONSENT)
    else:
        menu_keyboard = await create_menu_keyboard(user_language, buttons)
        await message.answer(await translate_text("You cannot resubmit your application while your previous application"
                                                  "is under review!", 'en', user_language, cache=True),
                             reply_markup=menu_keyboard)


async def finish_consent(message: Message, state: FSMContext, buttons):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    menu_keyboard = await create_menu_keyboard(user_language, buttons)
    await message.answer(await translate_text("You cannot submit an application without consent to the processing of your"
                                              "data.", 'en', user_language, cache=True),
                         reply_markup=menu_keyboard)
    await state.clear()


async def process_consent(message: Message, state: FSMContext):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    current_year = datetime.now().year
    
    await state.update_data(telegram_id=message.from_user.id)
    await message.answer(await translate_text("Thank you for your agreement! Now let's gather the necessary information.",
                                              'en', user_language, cache=True))
    
    await message.answer(await translate_text(f"Please note:\n- Entry into the country: after 01.02.{current_year}!\n"
                                              f"- The training lasts until the end of June {current_year+1} years!",
                                              'en', user_language, cache=True))
    
    await message.answer(await translate_text("Enter your last name.", 'en', user_language, cache=True))
    await state.set_state(StepsApply.WAITING_FOR_PERSONAL_INFO)


async def process_personal_info(message: Message, state: FSMContext, buttons):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    date_pattern = re.compile(r'(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])-\d{4}$')
    if 'last_name' not in data:
        if message.text.isalpha():
            await state.update_data(last_name=message.text.capitalize())
            await message.answer(await translate_text("Great! Now enter your name.", 'en', user_language, cache=True))
        else:
            await message.answer(await translate_text("The last name must contain only letters!", 'en', user_language, cache=True))

    elif 'first_name' not in data:
        if message.text.isalpha():
            await state.update_data(first_name=message.text.capitalize())
            await message.answer(await translate_text("Enter the country in which you live.", 'en', user_language, cache=True))
        else:
            await message.answer(await translate_text("The name must contain only letters!", 'en', user_language, cache=True))

    elif 'country' not in data:
        if message.text.isalpha():
            await state.update_data(country=message.text.capitalize())
            await message.answer(await translate_text("Enter your date of birth (in MM-DD-YYYY format).", 'en',
                                                      user_language, cache=True))
        else:
            await message.answer(await translate_text("The name of the country must contain only letters!", 'en',
                                                      user_language, cache=True))

    elif 'date_of_birth' not in data:
        if not date_pattern.match(message.text):
            await message.answer(
                await translate_text("Please enter your date of birth in MM-DD-YYYY format.", 'en', user_language, cache=True))
        else:
            date_of_birth = datetime.strptime(message.text, '%m-%d-%Y')
            current_date = datetime.now()
            age = current_date.year - date_of_birth.year - (
                        (current_date.month, current_date.day) < (date_of_birth.month, date_of_birth.day))
            if 16 <= age < 18:
                await state.update_data(date_of_birth=message.text)
                await message.answer(await translate_text("*Please note that if you are under 18 years old, then you must"
                                                          "have an official representative in Russia to conclude a"
                                                          "contract!*\n Enter your contact phone number.",
                                                          'en', user_language, cache=True))
                
            elif 18 <= age <= 100:
                await state.update_data(date_of_birth=message.text)
                await message.answer(await translate_text("Enter your contact phone number.", 'en', user_language, cache=True))
                
            else:
                menu_keyboard = await create_menu_keyboard(user_language, buttons)
                await message.answer(await translate_text("Age limits for submitting an application: 18+ years old!",
                                                          'en', user_language, cache=True), reply_markup=menu_keyboard)
                await state.clear()

    elif 'contact_phone' not in data:
        if await validate_phone_number(message.text):
            await state.update_data(contact_phone=message.text)
            await message.answer(await translate_text("Enter your email address.", 'en', user_language, cache=True))
        else:
            await message.answer(await translate_text("An incorrect phone number has been entered!", 'en',
                                                      user_language, cache=True))

    elif 'email' not in data:
        if await is_valid_email(message.text):
            await state.update_data(email=message.text)
            await message.answer(await translate_text("Which country did you study in before?", 'en',
                                                      user_language, cache=True))
        else:
            await message.answer(await translate_text("You have entered an incorrect email!", 'en',
                                                      user_language, cache=True))

    elif 'previous_education_country' not in data:
        if message.text.isalpha():
            await state.update_data(previous_education_country=message.text.capitalize())
            await message.answer(await translate_text("Send a passport photo in PDF or JPG format.", 'en',
                                                      user_language, cache=True))
            await state.set_state(StepsApply.WAITING_FOR_PASSPORT)
        else:
            await message.answer(await translate_text("The name of the country must contain only letters!", 'en',
                                                      user_language, cache=True))


async def process_passport_data(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        destination = await make_dir(data, 'passport.jpg')
        type = 'jpg'
    elif message.document and message.document.mime_type == 'application/pdf':
        file = await bot.get_file(message.document.file_id)
        destination = await make_dir(data, 'passport.pdf')
        type = 'pdf'
    else:
        await message.answer(await translate_text("Send your passport in JPG or PDF format!", 'en',
                                                  user_language, cache=True))
        return

    await bot.download_file(file.file_path, destination)
    try:
        passport_text = file_base64_to_text(destination, type)
    except Exception as e:
        logging.error(f"Ошибка при конвертации паспорта в формате {type} в текст: {e}")
        passport_text = ''

    await state.update_data(passport=destination, passport_text=passport_text)

    await message.answer(await translate_text("Send a photo of your passport translated into Russian in PDF or JPG format.",
                                              'en', user_language, cache=True))
    await state.set_state(StepsApply.WAITING_FOR_RU_PASSPORT)


async def process_ru_passport_data(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        destination = await make_dir(data, 'ru_passport.jpg')
        type = 'jpg'
    elif message.document and message.document.mime_type == 'application/pdf':
        file = await bot.get_file(message.document.file_id)
        destination = await make_dir(data, 'ru_passport.pdf')
        type = 'pdf'
    else:
        await message.answer(await translate_text("Send your passport translated into Russian in JPG or PDF format!",
                                                  'en', user_language, cache=True))
        return

    await bot.download_file(file.file_path, destination)

    try:
        ru_passport_text = file_base64_to_text(destination, type)
    except Exception as e:
        logging.error(f"Ошибка при конвертации переведенного паспорта в формате {type} в текст: {e}")
        ru_passport_text = ''

    await state.update_data(ru_passport=destination, ru_passport_text=ru_passport_text)

    await message.answer(await translate_text("Send a photo of the completed and signed visa application form in PDF or"
                                              "JPG format.", 'en', user_language, cache=True))
    await state.set_state(StepsApply.WAITING_FOR_VISA)


async def process_visa_application_form_data(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        destination = await make_dir(data, 'visa.jpg')
        type = 'jpg'
    elif message.document and message.document.mime_type == 'application/pdf':
        file = await bot.get_file(message.document.file_id)
        destination = await make_dir(data, 'visa.pdf')
        type = 'pdf'
    else:
        await message.answer(await translate_text("Send the completed and signed visa application form in PDF or JPG format!",
                                                  'en', user_language, cache=True))
        return

    await bot.download_file(file.file_path, destination)

    try:
        visa_text = file_base64_to_text(destination, type)
    except Exception as e:
        logging.error(f"Ошибка при конвертации ВИЗы в формате {type} в текст: {e}")
        visa_text = ''

    await state.update_data(visa=destination, visa_text=visa_text)

    await message.answer(await translate_text("Send a photo of a bank statement in your name with an account balance of"
                                              "$4,500 or the equivalent in local currency in PDF or JPG format.",
                                              'en', user_language, cache=True))
    await state.set_state(StepsApply.WAITING_FOR_BANK_STATEMENT)


async def process_bank_statement_data(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        destination = await make_dir(data, 'bank_statement.jpg')
        type = 'jpg'
    elif message.document and message.document.mime_type == 'application/pdf':
        file = await bot.get_file(message.document.file_id)
        destination = await make_dir(data, 'bank_statement.pdf')
        type = 'pdf'
    else:
        await message.answer(await translate_text("Send a bank statement in your name with an account balance of $4,500 or"
                                                  "the equivalent in local currency in PDF or JPG format!",
                                                  'en', user_language, cache=True))
        return

    await bot.download_file(file.file_path, destination)

    try:
        bank_statement_text = file_base64_to_text(destination, type)
    except Exception as e:
        logging.error(f"Ошибка при конвертации выписки с банковского счета в формате {type} в текст: {e}")
        bank_statement_text = ''

    await state.update_data(bank_statement=destination, bank_statement_text=bank_statement_text)

    await message.answer(await translate_text("Are you applying for yourself?", 'en', user_language),
                        reply_markup=for_whom_keyboard)
    await state.set_state(StepsApply.WAITING_FOR_TYPE)


async def process_application_type(message: Message, state: FSMContext):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    if message.text == "For myself":
        await state.update_data(application_for_self=True)
    elif message.text == "For another person":
        await state.update_data(application_for_self=False)
    await message.answer(await translate_text("Would you like to add any comments to your application? If yes, write it in "
                                              "the chat, if not, click on the button.", 'en', user_language, cache=True),
                         reply_markup=no_keyboard)
    await state.set_state(StepsApply.WAITING_FOR_COMMENTS)


async def process_agree_comments(message: Message, state: FSMContext):
    data = await state.get_data()
    user_language = data.get('user_language', 'en')
    if 'No' in message.text:
        await state.update_data(comments=' ')
    else:
        await state.update_data(comments=message.text)
    await state.update_data(status='awaiting review')
    await message.answer(await translate_text("Do you really want to apply?", 'en', user_language, cache=True),
                         reply_markup=yes_or_no_keyboard)
    await state.set_state(StepsApply.WAITING_FOR_APPLY)


async def finish_apply(message: Message, applications_middleware: ApplicationsMiddleware, bot: Bot, user_language,
                       admins_list, operators, state: FSMContext, buttons):
    if 'Yes' in message.text:
        data = await state.get_data()
        
        admins_id = [admin['user_id'] for admin in admins_list]

        operators_id = list(operator_id for operator_id, v in operators.items())

        ids = admins_id + operators_id
    
        last_name = data['last_name']
        first_name = data['first_name']
        user_id = data['telegram_id']
        review_keyboard = await review_kb(user_id, user_language, last_name, first_name)
        
        del data['user_language']
        result = await applications_middleware.add_application_to_db(data)
        
        if result:
            menu_keyboard = await create_menu_keyboard(user_language, buttons)
            await message.answer(await translate_text("Thanks! Your application has been submitted for consideration.",
                                                      'en', user_language, cache=True),
                                 reply_markup=menu_keyboard)
            
            utc_plus_5 = timezone(timedelta(hours=5))
            current_time_ekb = datetime.now(utc_plus_5).time()
            
            if datetime.strptime('08:00', '%H:%M').time() <= current_time_ekb <= datetime.strptime('20:00', '%H:%M').time():
                for tg_id in ids:
                    await bot.send_message(tg_id, f'Пользователь {last_name} {first_name} '
                                                  f'подал заявление на рассмотрение!', reply_markup=review_keyboard)

            await applications_middleware.add_application(user_id, user_language, last_name, first_name)
        
        else:
            await message.answer(await translate_text("An error in submitting the application! Try again, or contact support",
                                                      'en', user_language, cache=True), reply_markup=contact_with_operator_keyboard)

    else:
        menu_keyboard = await create_menu_keyboard(user_language, buttons)
        await message.answer(await translate_text("Your application has not been saved!", 'en', user_language, cache=True),
                             reply_markup=menu_keyboard)
    await state.clear()
