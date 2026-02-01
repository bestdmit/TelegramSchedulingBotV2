from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import subjects
from keyboards import change_roles_keyboard

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
            callback_data=f"registered_user_change_role_{user_id}"
        )
        
        builder.button(
            text = "Предметы",
            callback_data=f"registered_user_change_subjects_{user_id}"
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
        
    async def process_change_role(self,callback: CallbackQuery):
        user_id = int(callback.data.split("_")[-1])
        user = await self.user_worker.get_user(user_id)
        
        await callback.message.answer(
            "Выберите новые роли:",
            reply_markup=change_roles_keyboard(selected_roles=set(),selected_user_id=user_id)
        )

    async def process_role_toggle(self,callback: CallbackQuery):
        parts = callback.data.split(":")
        user_id = int(parts[1])
        clicked_role = parts[2]

        selected_roles = set()
        
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data.startswith("changed_role_tgl:"):
                    role_name = btn.callback_data.split(":")[-1]
                    if "✅" in btn.text:
                        selected_roles.add(role_name)

        if clicked_role in selected_roles:
            selected_roles.remove(clicked_role)
        else:
            selected_roles.add(clicked_role)

        await callback.message.edit_reply_markup(
            reply_markup=change_roles_keyboard(selected_roles, user_id)
        )
        await callback.answer()

    async def process_role_save(self,callback: CallbackQuery):
        user_id = int(callback.data.split(":")[-1])
        user_name = (await self.user_worker.get_user(user_id))["user_name"]
        final_roles = []
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data.startswith("changed_role_tgl:") and "✅" in btn.text:
                    final_roles.append(btn.callback_data.split(":")[-1])

        if not final_roles:
            await callback.answer("Выберите хотя бы одну роль!", show_alert=True)
            return
        
        roles_str = ",".join(final_roles)
        await self.user_worker.update_user(user_id,user_name, roles_str)
        await callback.message.answer(
            f"Роли Обновлены!\nПользователь ID {user_id}\nРоли: {roles_str}"
        )
        # await callback.answer()