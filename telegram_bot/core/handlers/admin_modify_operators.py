from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.keyboards.operators_list_kb import create_operators_list_kb
from core.utils.states_add_operator import StepsAddOperator
from core.middlewares.admins_middleware import AdminsMiddleware
from core.filters.isOperator import IsOperator


async def start_delete_operator(message: Message, operators):
    if len(operators) == 0:
        await message.answer('Операторы отсутствуют!', reply_markup=admin_menu_keyboard)
    else:
        operators_keyboard = await create_operators_list_kb(operators)
        await message.answer('Выберите пользователя, которого вы хотите лишить прав оператора:',
                             reply_markup=operators_keyboard)


async def finish_delete_operator(call: CallbackQuery, admins_middleware: AdminsMiddleware, is_operator: IsOperator):
    operator_id = int(call.data.split('_')[-1])
    await admins_middleware.del_operator(operator_id)
    await is_operator.delete_operator(operator_id)

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await call.bot.delete_message(chat_id, message_id)

    await call.message.answer('Пользователь был лишен прав оператора.', reply_markup=admin_menu_keyboard)


async def start_add_operator(message: Message, state: FSMContext):
    await message.answer('Отправьте контакт пользователя, которого Вы хотите наделить правами оператора.')
    await state.set_state(StepsAddOperator.GET_OPERATOR)


async def finish_add_operator(message: Message, state: FSMContext, admins_middleware: AdminsMiddleware,
                              is_operator: IsOperator):
    if message.contact:
        user_id = message.contact.user_id
        first_name = message.contact.first_name
        last_name = message.contact.last_name if message.contact.last_name else ""

        if not last_name:
            await state.update_data(user_id=user_id, first_name=first_name, contact=message.contact)
            await message.answer("Отправьте фамилию оператора.")
            await state.set_state(StepsAddOperator.GET_LAST_NAME)
        else:
            full_name = first_name + " " + last_name
            await admins_middleware.add_operator(user_id, first_name, last_name, message.contact)
            await is_operator.add_operator(user_id)

            await message.answer(f"Пользователь {full_name} успешно добавлен в список операторов!",
                                 reply_markup=admin_menu_keyboard)
            await state.clear()
    else:
        await message.answer("Пожалуйста, отправьте контакт для импорта, используя кнопку 'Поделиться контактом' на"
                             "странице пользователя.")


async def get_last_name_operator(message: Message, state: FSMContext, admins_middleware: AdminsMiddleware,
                                 is_operator: IsOperator):
    data = await state.get_data()
    user_id = data['user_id']
    first_name = data["first_name"]
    last_name = message.text
    full_name = first_name + ' ' + last_name
    contact = data['contact']

    await admins_middleware.add_operator(user_id, first_name, last_name, contact)
    await is_operator.add_operator(user_id)

    await message.answer(f"Пользователь {full_name} успешно добавлен в список операторов!",
                         reply_markup=admin_menu_keyboard)
    await state.clear()
