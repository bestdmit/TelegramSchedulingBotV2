from typing import Union
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.registerSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_parents import ParentsDataBaseWorker
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


#Обработка списка всех пользователей
@admin_router.message(Command("all_users"))
async def show_all_users_handler(message: Message,userWorker:UsersDataBaseWorker):
    all_service = AdminServicesFactory.create_admin_service_for_all_users(user_worker=userWorker)
    await all_service.show_all_users(message=message)

@admin_router.callback_query(F.data.startswith("registered_user_info"))
async def process_redistered_user_click(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    user_id = callback.data.split("_")[-1]
    reg_user = await userWorker.get_user(int(user_id))
    roles = reg_user["roles"]
    teacher_subjects = reg_user["teacher_subjects"]
    student_subjects = reg_user["student_subjects"]
async def process_redistered_user_click_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    all_service = AdminServicesFactory.create_admin_service_for_all_users(user_worker=userWorker)
    await all_service.process_redistered_user_click(callback=callback)

# Обработка смены ролей
@admin_router.callback_query(F.data.startswith("registered_user_change_role"))
async def process_give_role_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    all_service = AdminServicesFactory.create_admin_service_for_all_users(user_worker=userWorker)
    await all_service.process_change_role(callback=callback)

@admin_router.callback_query(F.data.startswith("changed_role_tgl"))
async def changed_process_role_toggle_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    all_service = AdminServicesFactory.create_admin_service_for_all_users(user_worker=userWorker)
    await all_service.process_role_toggle(callback=callback)

@admin_router.callback_query(F.data.startswith("changed_role_save:"))
async def process_role_save_handler(callback: CallbackQuery, userWorker: UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_all_users(userWorker)
    await service.process_role_save(callback=callback)

# Обработка смены предметов

@admin_router.callback_query(F.data.startswith("registered_user_change_subjects"))
async def process_change_subjects_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    all_service = AdminServicesFactory.create_admin_service_for_all_users(user_worker=userWorker)
    await all_service.process_change_subjects(callback=callback)
    
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
@admin_router.callback_query(F.data.startswith("changed_subject_tgl"))
async def process_subject_toggle_handler(callback: CallbackQuery,userWorker:UsersDataBaseWorker):
    all_service = AdminServicesFactory.create_admin_service_for_all_users(user_worker=userWorker)
    await all_service.process_subject_toggle(callback=callback)

@admin_router.callback_query(F.data.startswith("changed_subjects_save:"))
async def process_role_save_handler(callback: CallbackQuery, userWorker: UsersDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_all_users(userWorker)
    await service.process_subjects_save(callback=callback)

#Обработка работы с родителями
@admin_router.message(Command("parent_hub"))
@admin_router.callback_query(F.data.startswith("back_to_parentslist"))
async def show_users_parents_handler(event: Union[Message, CallbackQuery],
                                     userWorker:UsersDataBaseWorker,
                                     parentsWorker:ParentsDataBaseWorker
                                     ):
    service = AdminServicesFactory.create_admin_service_for_parent_users(userWorker,parentsWorker)
    message = event if isinstance(event, Message) else event.message
    await service.list_users(message=message)

@admin_router.callback_query(F.data.startswith("parent_info"))
async def parent_info(callback:CallbackQuery,
                      userWorker:UsersDataBaseWorker,
                      parentsWorker:ParentsDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_parent_users(userWorker,parentsWorker)
    await service.parent_info(callback=callback)

@admin_router.callback_query(F.data.startswith("choose_childrens_for_associating_parent"))
async def show_childrens(callback:CallbackQuery,
                      userWorker:UsersDataBaseWorker,
                      parentsWorker:ParentsDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_parent_users(userWorker,parentsWorker)
    await service.list_users(message=callback.message,
                             for_childrens=True,
                             parent_id=int(callback.data.split("_")[-1]))
    
@admin_router.callback_query(F.data.startswith("child_tgl"))
async def child_tgl_for_parent(callback:CallbackQuery,
                      userWorker:UsersDataBaseWorker,
                      parentsWorker:ParentsDataBaseWorker):
    service = AdminServicesFactory.create_admin_service_for_parent_users(userWorker,parentsWorker)
    await service.child_tgl(callback=callback)

@admin_router.callback_query(F.data.startswith("associating_children"))
async def child_tgl_for_parent(callback:CallbackQuery,
                      userWorker:UsersDataBaseWorker,
                      parentsWorker:ParentsDataBaseWorker,
                    bot: Bot):
    service = AdminServicesFactory.create_admin_service_for_parent_users(userWorker,parentsWorker)
    await service.add_parent_child_relation(callback=callback,bot=bot)


