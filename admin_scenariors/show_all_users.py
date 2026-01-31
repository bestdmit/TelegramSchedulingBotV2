from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import subjects
from keyboards import get_subjects_keyboard, get_roles_keyboard

class AllUserServices:
    """Работа со списком всех пользователей"""

    def __init__(self,user_worker:UsersDataBaseWorker):
        self.user_worker = user_worker

    async def show_all_users(self,message: Message):
        users = await self.user_worker.get_all_users()
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
        
    async def process_redistered_user_click(self,callback: CallbackQuery):
        user_id = callback.data.split("_")[-1]
        reg_user = await self.user_worker.get_user(int(user_id))
        roles = reg_user["roles"]
        subjects = reg_user["subjects"]

        builder = InlineKeyboardBuilder()
        builder.button(
            text = "Роли",
            callback_data=f"registered_user_give_role_{user_id}"
        )
        
        builder.button(
            text = "Предметы",
            callback_data=f"registered_user_subjects_{user_id}"
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
        if subjects:
            user_info+=f"Предметы: {subjects}\n"
        else:
            ser_info+=f"Предметы НЕ НАЗНАЧЕНЫ\n"
        await callback.message.answer(
            user_info,
            reply_markup=builder.as_markup())