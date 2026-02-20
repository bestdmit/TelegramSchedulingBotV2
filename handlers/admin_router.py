from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.RegisterSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import admin_ids,roles, subjects
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton,CallbackQuery
from keyboards import get_subjects_keyboard, get_roles_keyboard
from admin_scenariors.adminFactory import AdminServicesFactory
from aiogram import Bot

admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(admin_ids))

@admin_router.message(Command("show"))
async def show_users_without_roles_handler(message: Message,userWorker:UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.show_users_without_roles(message)
    

@admin_router.callback_query(F.data.startswith("user_info"))
async def process_simple_user_click_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_simple_user_click(callback=callback)
    
@admin_router.callback_query(F.data.startswith("simple_user_give_role"))
async def process_give_role_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_give_role(callback=callback)


@admin_router.callback_query(F.data.startswith("role_tgl:"))
async def process_role_toggle_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_role_toggle(callback=callback)

@admin_router.callback_query(F.data.startswith("role_save:"))
async def process_role_save_handler(callback: CallbackQuery, userWorker: UsersDataBaseWorker, bot: Bot):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_role_save(callback=callback, bot = bot)


    
@admin_router.callback_query(F.data.startswith("subject_tgl:"))
async def process_subject_toggle_handler(callback: CallbackQuery, userWorker: UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_subject_toggle(callback=callback)
    

@admin_router.callback_query(F.data.startswith("subjects_save:"))
async def process_subjects_save_handler(callback: CallbackQuery, userWorker: UsersDataBaseWorker, bot: Bot):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_subjects_save(callback=callback, bot = bot)

@admin_router.message(Command("all_users"))
async def show_all_users(message: Message,userWorker:UsersDataBaseWorker):
    users = await userWorker.get_all_users()
    builder = InlineKeyboardBuilder()

    for user in users:
        builder.button(
            text=user['user_name'],
            callback_data=f"registered_user_info_{user['user_id']}"
        )
    builder.adjust(1)

    await message.answer(
        "Список всех пользователей",
        reply_markup=builder.as_markup()
    )

@admin_router.callback_query(F.data.startswith("registered_user_info"))
async def process_redistered_user_click(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    user_id = callback.data.split("_")[-1]
    reg_user = await userWorker.get_user(int(user_id))
    roles = reg_user["roles"]
    teacher_subjects = reg_user["teacher_subjects"]
    student_subjects = reg_user["student_subjects"]

    builder = InlineKeyboardBuilder()
    builder.button(
        text = "Роли",
        callback_data=f"registered_user_give_role_{user_id}"
    )
    
    # builder.button(
    #     text = "Предметы",
    #     callback_data=f"registered_user_subjects_{user_id}"
    # )
    
    # ДОБАВЛЕНЫ: отдельные кнопки для каждой роли
    if "teacher" in roles:
        builder.button(
            text="Предметы преподавателя",
            callback_data=f"teacher_give_subjects_{user_id}"
        )
    
    if "student" in roles:
        builder.button(
            text="Предметы ученика",
            callback_data=f"student_give_subjects_{user_id}"
        )
        
    builder.adjust(2)
    await callback.message.delete()
    await callback.answer()

    user_info = f"Пользователь: {reg_user['user_name']}\n"
    user_info+=f"User Id: {user_id}\n"
    if len(roles)>0:
        user_info+=f"Роли: {roles}\n"
    else:
        user_info+=f"Роли НЕ НАЗНАЧЕНЫ\n"
    if teacher_subjects:
        teacher_names = [subjects.get(s_id, f"Предмет {s_id}") 
                        for s_id in teacher_subjects.split(',') if s_id]
        user_info += f"Предметы преподавателя: {', '.join(teacher_names)}\n"
    
    if student_subjects:
        student_names = [subjects.get(s_id, f"Предмет {s_id}") 
                        for s_id in student_subjects.split(',') if s_id]
        user_info += f"Предметы ученика: {', '.join(student_names)}\n"
    if (not student_subjects) and (not teacher_subjects):
        user_info+=f"Предметы НЕ НАЗНАЧЕНЫ\n"
    await callback.message.answer(
        user_info,
        reply_markup=builder.as_markup())

@admin_router.callback_query(F.data.startswith("teacher_give_subjects_"))
async def process_teacher_subjects_handler(callback: CallbackQuery, userWorker: UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_teacher_subjects(callback=callback)

@admin_router.callback_query(F.data.startswith("student_give_subjects_"))
async def process_student_subjects_handler(callback: CallbackQuery, userWorker: UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_simple_users(userWorker)
    await service.process_student_subjects(callback=callback)