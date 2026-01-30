from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.registerSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import admin_ids,roles, Teacher_Subjects
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton,CallbackQuery
from keyboards import get_subjects_keyboard, get_roles_keyboard


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
        current_subjects = simple_user.get("teacher_subjects", "")
        if current_subjects==False or current_subjects=="":
            builder.button(
            text = "Добавить предметы преподавателю",
            callback_data=f"teacher_give_subjects_{user_id}"
        )
    if ("student" in roles) and (roles == "" or roles==None):
        current_subjects = simple_user.get("teacher_subjects", "")
        if current_subjects==False or current_subjects=="":
            builder.button(
            text = "Добавить предметы ученику",
            callback_data=f"teacher_give_subjects_{user_id}"
        )
        
    builder.adjust(2)
    await callback.message.delete()
    await callback.answer()

    user_info = f"Пользователь: {simple_user['user_name']}\n"
    user_info+=f"User Id: {user_id}\n"
    if roles == True:
        user_info+=f"Роли: {roles}\n"
    else:
        user_info+=f"Роли НЕ НАЗНАЧЕНЫ\n"

    if (roles and "teacher" in roles) or (roles and "student" in roles):
        subjects = simple_user.get("teacher_subjects", "")
        if subjects:
            subjects_names = []
            for Sub_Id in subjects.split(','):
                if Sub_Id.strip():
                    subjects_names.append(Teacher_Subjects.get(Sub_Id, f"Предмет {Sub_Id}"))
            user_info += f"Предметы: {', '.join(subjects_names)}\n"
        else:
            user_info+=f"Предметы не назначены\n"
    await  callback.message.answer(
        user_info,
        reply_markup=builder.as_markup())
    
@admin_router.callback_query(F.data.startswith("simple_user_give_role"))
async def process_give_role(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    user_id = int(callback.data.split("_")[-1])
    simple_user = await userWorker.get_user(user_id)
    
    await callback.message.answer(
        "Выберите роли:",
        reply_markup=get_roles_keyboard(selected_roles=set(),selected_user_id=user_id)
    )


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
    if ("teacher" in final_roles) or ("student" in final_roles):
        if "teacher" in final_roles:
            await callback.message.answer(
                f"Роли добавлены ✅\n"
                f"Пользователь: {user_name} (ID: {user_id})\n"
                f"Роли: {roles_str}\n"
                f"Выберите предмет для преподавателя:",
                reply_markup=get_subjects_keyboard(selected_subjects=set(), user_id=user_id)
            )
        elif "student" in final_roles:
            await callback.message.answer(
                f"Роли добавлены ✅\n"
                f"Пользователь: {user_name} (ID: {user_id})\n"
                f"Роли: {roles_str}\n"
                f"Выберите предмет для ученика:",
                reply_markup=get_subjects_keyboard(selected_subjects=set(), user_id=user_id)
            )
    else:
        await callback.message.answer(
            f"Роли добавлены ✅\n"
            f"Пользователь: {user_name}\n"
            f"User ID: {user_id}\n"
            f"Роли: {roles_str}"
        )
    # await callback.message.answer(
    #     f"Роли добавлены!\nПользователь ID {user_id}\nРоли: {roles_str}"
    # )
    await callback.answer()


    
@admin_router.callback_query(F.data.startswith("subject_tgl:"))
async def process_subject_toggle(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[1])
    clicked_subject_id = parts[2]
    
    selected_subjects = set()
    for row in callback.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data.startswith("subject_tgl:"):
                subject_id = btn.callback_data.split(":")[-1]
                if "✅" in btn.text:
                    selected_subjects.add(subject_id)
    if clicked_subject_id in selected_subjects:
        selected_subjects.remove(clicked_subject_id)
    else:
        selected_subjects.add(clicked_subject_id)
    
    await callback.message.edit_reply_markup(
        reply_markup=get_subjects_keyboard(selected_subjects, user_id)
    )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("subjects_save:"))
async def process_subjects_save(callback: CallbackQuery, userWorker: UsersDataBaseWorker):
    user_id = int(callback.data.split(":")[-1])
    user = await userWorker.get_user(user_id)
    
    selected_subjects = []
    for row in callback.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data.startswith("subject_tgl:") and "✅" in btn.text:
                subject_id = btn.callback_data.split(":")[-1]
                selected_subjects.append(subject_id)
    
    if not selected_subjects:
        await callback.answer("Нужно дать пользователю хотя бы один предмет ", show_alert=True)
        return
    
    subjects_str = ",".join(selected_subjects)
    
    success = await userWorker.update_user(
        user_id=user_id,
        teacher_subjects=subjects_str
    )
    
    if success:
        subject_names = []
        for subj_id in selected_subjects:
            subject_names.append(Teacher_Subjects.get(subj_id, f"Предмет {subj_id}"))
        
        await callback.message.delete()
        await callback.message.answer(
            f"✅ Предметы успешно добавлены!\n\n"
            f"Преподаватель: {user['user_name']}\n"
            f"User ID: {user_id}\n"
            f"Предметы: {', '.join(subject_names)}\n"
            f"ID предметов: {subjects_str}"
        )
    else:
        await callback.answer("Ошибка при сохранении предметов!", show_alert=True)
    
    await callback.answer()