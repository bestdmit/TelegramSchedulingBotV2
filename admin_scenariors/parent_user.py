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

    async def list_users(self,message:Message,for_childrens:bool=None,parent_id:int=None,
                         for_childrens_booking:bool=None):
        '''Список всех пользователей'''
        all_users = await self.user_worker.get_all_users()
        builder = InlineKeyboardBuilder()
        parent_name = None
        if for_childrens:
            childrens = await self.parent_worker.get_children(parent_id)
            parent_name = (await self.user_worker.get_user(parent_id))['user_name']
            for child in all_users:
                builder.button(
                    text=("✅" if child['user_id'] in childrens else "")+child['user_name'],
                    callback_data=f"child_tgl_{child['user_id']}_parent_{str(parent_id)}"
                )
        else:
            for parent in all_users:
                builder.button(
                    text=parent['user_name'],
                    callback_data=f"parent_info_{parent['user_id']}"
                )
        builder.adjust(1)
        if for_childrens:
            await message.edit_text(
            f"Выбранный родитель:{parent_name}\nВыберите ребёнка:",
            reply_markup=builder.as_markup()
        )
        else:
            await message.answer(
                "Выберите пользователя:",
                reply_markup=builder.as_markup()
            )
    async def parent_info(self,callback:CallbackQuery):
        '''Информация о выбранном родителе'''
        parent_id = int(callback.data.split("_")[-1])
        parent_name = (await self.user_worker.get_user(parent_id))['user_name']
        childrens = await self.parent_worker.get_children(parent_id)

        res = f"Выбранный родитель:{parent_name}\nДети:\n"
        for children_id in childrens:
            res += f"{(await self.user_worker.get_user(children_id))['user_name']}\n"

        builder = InlineKeyboardBuilder()
        builder.button(
            text="Назад",
            callback_data=f"back_to_parentslist"
        )
        builder.button(
            text="Добавить детей",
            callback_data=f"choose_childrens_for_associating_parent_{parent_id}"
        )
        
        builder.adjust(2)
        return await callback.message.edit_text(
            text=res,
            reply_markup=builder.as_markup()
        )
    
    async def child_tgl(self,callback:CallbackQuery):
        '''Нажатие на ребенка при выборе добавления связи родитель-ребенок'''
        try:
            child_id = int(callback.data.split("_")[2])
            child_name = (await self.user_worker.get_user(child_id))['user_name']
            parent_id = int(callback.data.split("_")[-1])
            parent_name = (await self.user_worker.get_user(parent_id))['user_name']
            res = ("Подтвердить связь?\n"+
                   f"Ребёнок:\n" +
                   f"Имя: {child_name}\n" +
                   f"ID: {child_id}\n"
                   f"Для родителя:\n" + 
                   f"Имя: {parent_name}\n" +
                   f"ID: {parent_id}\n"
                   )
            builder = InlineKeyboardBuilder()
            builder.button(
                text="❌ Нет",
                callback_data=f"choose_childrens_for_associating_parent_{parent_id}"
            )
            builder.button(
                text="✅ Да",
                callback_data=f"associating_children_{child_id}_parent_{parent_id}"
            )
            await callback.message.edit_text(
                text=res,
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            print(f"Проблема подтверждения связи родитель-ребенок: {e}")

    
    async def add_parent_child_relation(self,callback:CallbackQuery,bot: Bot = None):
        '''Добавление связи родитель-ребенок'''
        # Пример коллбэка associating_children_{}_parent_{}
        try:
            parent_id = int(callback.data.split("_")[-1])
            children_id = int(callback.data.split("_")[-3])
            children_name = (await self.user_worker.get_user(children_id))['user_name']
            res = await self.parent_worker.add_parent_child_relation(parent_id,children_id)
            if res:
                await callback.message.edit_text("✅ Ребенок успешно привязан к родителю.")
                new_menu = get_main_menu(parent=True)
                await bot.send_message(
                    chat_id=parent_id,
                    text=f"Вам назначен ребёнок: {children_name}\n"
                            f"Ваше меню обновлено",
                    reply_markup=new_menu
                )
            else:
                await callback.message.edit_text("⚠️ Не удалось добавить связь.")
        except Exception as e:
            print(f"Проблема с связывание родителя-ребенка: {e}")

    
        
