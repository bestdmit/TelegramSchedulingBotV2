from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.registerSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import admin_ids,roles
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton,CallbackQuery

admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(admin_ids))

@admin_router.message(Command("show"))
async def show_users_without_roles(message: Message,userWorker:UsersDataBaseWorker):
    simple_users = await userWorker.get_simple_users()
    builder = InlineKeyboardBuilder()

    for user in simple_users:
        builder.button(
            text=user['user_name'],
            callback_data=f"user_info_{user['user_id']}"
        )
    builder.adjust(1)

    await message.answer(
        "Выберите юзера для заполнения",
        reply_markup=builder.as_markup()
    )

@admin_router.callback_query(F.data.startswith("user_info"))
async def process_simple_user_click(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    user_id = callback.data.split("_")[-1]
    simple_user = await userWorker.get_user(int(user_id))
    roles = simple_user["roles"]
    teacher_subjects = simple_user["teacher_subjects"]

    builder = InlineKeyboardBuilder()
    if roles == "" or roles == None:
        builder.button(
            text = "Добавить роль",
            callback_data=f"simple_user_give_role_{user_id}"
        )
    if ("teacher" in roles) and (roles == "" or roles==None):
        builder.button(
            text = "Добавить предметы преподавателю",
            callback_data=f"teacher_give_subjects_{user_id}"
        )
    builder.adjust(2)
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer(
        f"Выберите дествие с пользователем {simple_user["user_name"]}",
        reply_markup=builder.as_markup()
        )
    
@admin_router.callback_query(F.data.startswith("simple_user_give_role"))
async def process_give_role(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    user_id = int(callback.data.split("_")[-1])
    simple_user = await userWorker.get_user(user_id)
    
    await callback.message.answer(
        "Выберите роли:",
        reply_markup=get_roles_keyboard(selected_roles=set(),selected_user_id=user_id)
    )


def get_roles_keyboard(selected_roles:set,selected_user_id:int):
    builder = InlineKeyboardBuilder()

    for role in roles:
        label = f"{role}"
        if role in selected_roles:
            label = "✅ "+label
        builder.button(
            text = label,
            callback_data=f"role_tgl:{selected_user_id}:{role}"
        )
    builder.adjust(2)

    builder.row(types.InlineKeyboardButton(
        text="Применить ✅", 
        callback_data=f"role_save:{selected_user_id}"
        )
    )
    return builder.as_markup()

@admin_router.callback_query(F.data.startswith("role_tgl:"))
async def process_role_toggle(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[1])
    clicked_role = parts[2]

    selected_roles = set()
    
    for row in callback.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data.startswith("role_tgl:"):
                role_name = btn.callback_data.split(":")[-1]
                if "✅" in btn.text:
                    selected_roles.add(role_name)

    if clicked_role in selected_roles:
        selected_roles.remove(clicked_role)
    else:
        selected_roles.add(clicked_role)

    await callback.message.edit_reply_markup(
        reply_markup=get_roles_keyboard(selected_roles, user_id)
    )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("role_save:"))
async def process_role_save(callback: CallbackQuery, userWorker: UsersDataBaseWorker):
    user_id = int(callback.data.split(":")[-1])
    user_name = (await userWorker.get_user(user_id))["user_name"]
    final_roles = []
    for row in callback.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data.startswith("role_tgl:") and "✅" in btn.text:
                final_roles.append(btn.callback_data.split(":")[-1])

    if not final_roles:
        await callback.answer("Выберите хотя бы одну роль!", show_alert=True)
        return
    
    roles_str = ",".join(final_roles)
    await userWorker.update_user(user_id,user_name, roles_str)

    await callback.message.delete()
    await callback.message.answer(
        f"Роли добавлены!\nПользователь ID {user_id}\nРоли: {roles_str}"
    )
    await callback.answer()
    
