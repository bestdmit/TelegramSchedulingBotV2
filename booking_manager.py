from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
from config import subjects
from keyboards import get_main_menu
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Dict, Any

class BookingManager:
    def __init__(self, user_worker: UsersDataBaseWorker, booking_worker: BookingsDataBaseWorker):
        self.user_worker = user_worker
        self.booking_worker = booking_worker
    
    async def init_booking_proccess(self, message: Message, state: FSMContext) -> Dict[str, Any]:
        user_id = message.from_user.id
        if not await self.user_worker.check_user(user_id):
            return{
                "success": False,
                "message": "Для бронирования времени нужно зарегестрироваться",
                "next_step": None
            }
        user_data = await self.user_worker.get_user(user_id)
        if not user_data:
            return {
                "success": False,
                "message": "Ошибка получения данных",
                "next_step": None
            }
        roles = user_data.get("roles", "")
        if not roles:
            return {
                "success": False,
                "message": "У вас нет ролей",
                "next_step": None
            }
        subjects = user_data.get("subjects", "")
        if not subjects:
            return {
                "success": False,
                "message": "У вас нет предметов",
                "next_step": None
            }
        user_name =  user_data.get('user_name', '')
        await state.update_data({
            'booking_user_id': user_id,
            'booking_user_name':user_name,
            'booking_roles': roles,
            'booking_subjects': subjects,
            'booking_step': 'initial'
        })
        message_text = self.generate_success_message(user_name,roles)
        
        return {
            "success": True,
            "message": message_text,
            "user_data": user_data,
            "next_step": "selectr_role_or_subject",
        }

    def generate_success_message(self, user_name: str, roles: str) -> str:
        user_roles = [role.strip() for role in roles.split(',')]
        message = f"Привет, {user_name}\n"
        if "teacher" in roles and "student" in roles:
            message+="Вам назначены роли: \n"
            message+="Преподаватель, \n"
            message+="Ученик \n"
        elif "teacher" in roles:
            message+="Вам назначены роли: \n"
            message+="Преподаватель, \n"
        elif "student" in roles:
            message+="Вам назначены роли: \n"
            message+="Ученик \n"
            
        return message
        
async def start_booking_for_user(message: Message, state: FSMContext, user_worker: UsersDataBaseWorker, 
                                booking_worker: BookingsDataBaseWorker)-> Dict[str,Any]:
    manager = BookingManager(user_worker, booking_worker)
    return await manager.init_booking_proccess(message, state)