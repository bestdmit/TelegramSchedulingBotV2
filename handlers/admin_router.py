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
async def show_users_parents_handler(message: Message,
                                     userWorker:UsersDataBaseWorker,
                                     parentsWorker:ParentsDataBaseWorker
                                     ):
    service = AdminServicesFactory.create_admin_service_for_parent_users(userWorker,parentsWorker)
    await service.list_users(message=message)


