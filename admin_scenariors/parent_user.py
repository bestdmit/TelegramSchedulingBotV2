from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_parents import ParentsDataBaseWorker
from config import subjects,rolesRU
from keyboards import get_subjects_keyboard, get_roles_keyboard
from aiogram import Bot
from keyboards import get_main_menu
class ParentUserServices:
    """Работа с родителями"""

    def __init__(self,user_worker:UsersDataBaseWorker,parent_worker:ParentsDataBaseWorker):
        self.user_worker = user_worker
        self.parent_worker = parent_worker

    async def list_users(self,message:Message):
        all_users = await self.user_worker.get_all_users()
        builder = InlineKeyboardBuilder()

        for parent in all_users:
            builder.button(
                text=parent['user_name'],
                callback_data=f"parent_info_{parent['user_id']}"
            )
        builder.adjust(1)
        await message.answer(
            "Выберите пользователя:",
            reply_markup=builder.as_markup()
        )
    async def parent_info(self,callback:CallbackQuery):
        parent_id = int(callback.split("_")[-1])
        parent_name = (await self.user_worker.get_user(parent_id))['user_name']
        childrens = await self.parent_worker.get_children(parent_id)

        res = f"Выбранный пользователь:{parent_name}\nДети:\n"
        for children_id in childrens:
            res += f"{(await self.user_worker.get_user(children_id))['user_name']}\n"