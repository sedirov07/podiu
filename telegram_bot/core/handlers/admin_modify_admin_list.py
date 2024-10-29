from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.keyboards.admin_menu_kb import admin_menu_keyboard
from core.keyboards.admins_list_kb import create_admins_list_kb
from core.keyboards.admin_manage_kb import admin_manage_keyboard
from core.utils.states_add_admin import StepsAddAdmin
from core.middlewares.admins_middleware import AdminsMiddleware
from core.filters.isAdmin import IsAdmin


async def manage(message: Message):
    await message.answer('Выберите: ', reply_markup=admin_manage_keyboard)


async def start_delete_admin(message: Message, admins_list):
    user_id = message.from_user.id
    admins = [admin['user_id'] for admin in admins_list]
    if len(admins_list) == 1:
        await message.answer('Вы единственный администратор.', reply_markup=admin_menu_keyboard)
    elif user_id in admins:
        admins_list.pop(admins.index(user_id))
        admins_keyboard = await create_admins_list_kb(admins_list)
        await message.answer('Выберите пользователя, которого вы хотите лишить прав администратора:',
                             reply_markup=admins_keyboard)


async def finish_delete_admin(call: CallbackQuery, admins_middleware: AdminsMiddleware, is_admin: IsAdmin):
    admin_id = call.data.split('_')[-1]
    await admins_middleware.del_admin(admin_id)
    is_admin.delete_admin(admin_id)

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await call.bot.delete_message(chat_id, message_id)

    await call.message.answer('Пользователь был лишен прав администратора.', reply_markup=admin_menu_keyboard)


async def start_add_admin(message: Message, state: FSMContext):
    await message.answer('Отправьте контакт пользователя, которого Вы хотите наделить правами администратора.')
    await state.set_state(StepsAddAdmin.GET_ADMIN)


async def finish_add_admin(message: Message, state: FSMContext, admins_middleware: AdminsMiddleware, is_admin: IsAdmin):
    if message.contact:
        user_id = message.contact.user_id
        first_name = message.contact.first_name
        last_name = " " + message.contact.last_name if message.contact.last_name else ""
        full_name = first_name + last_name

        await admins_middleware.add_admin(user_id, full_name)
        is_admin.add_admin(user_id)

        await message.answer(f"Пользователь {full_name} успешно добавлен в список администраторов!")
        await state.clear()
    else:
        await message.answer("Пожалуйста, отправьте контакт для импорта, используя кнопку 'Поделиться контактом' на "
                             "странице пользователя.")
