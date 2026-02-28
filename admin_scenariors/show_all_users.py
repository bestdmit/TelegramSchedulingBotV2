from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import subjects
from keyboards import change_roles_keyboard,change_subjects_keyboard

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
        student_subjects = reg_user['student_subjects']
        teacher_subjects = reg_user['teacher_subjects']

        builder = InlineKeyboardBuilder()
        builder.button(
            text = "Роли",
            callback_data=f"registered_user_change_role_{user_id}"
        )
        
        builder.button(
            text = "Студ предметы",
            callback_data=f"registered_user_change_student_subjects_{user_id}"
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
        if len(student_subjects)>0:
            user_info+=f"Предметы ученика: {student_subjects}\n"
        if len(teacher_subjects)>0:
            user_info+=f"Предметы препода: {teacher_subjects}\n"
        if len(student_subjects)+len(teacher_subjects)==0:
            ser_info+=f"Предметы НЕ НАЗНАЧЕНЫ\n"
        await callback.message.answer(
            user_info,
            reply_markup=builder.as_markup())
        
    async def process_change_role(self,callback: CallbackQuery):
        user_id = int(callback.data.split("_")[-1])
        user = await self.user_worker.get_user(user_id)
        roles = user["roles"].split(',')
        await callback.message.answer(
            "Выберите новые роли:",
            reply_markup=change_roles_keyboard(selected_roles=set(roles),selected_user_id=user_id)
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
    
    async def process_change_subjects(self,callback: CallbackQuery):
        user_id = int(callback.data.split("_")[-1])
        user = await self.user_worker.get_user(user_id)
        subjects = user["student_subjects"].split(",")
        await callback.message.answer(
            f"Выбранный пользователь:{user["user_name"]}\nВыберите новые предметы:",
            reply_markup=change_subjects_keyboard(selected_subjects=set(subjects),user_id=user_id)
        )

    async def process_subject_toggle(self,callback: CallbackQuery):
        parts = callback.data.split(":")
        user_id = int(parts[1])
        clicked_subject_id = parts[2]
        
        selected_subjects = set()
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data.startswith("changed_subject_tgl:"):
                    subject_id = btn.callback_data.split(":")[-1]
                    if "✅" in btn.text:
                        selected_subjects.add(subject_id)
        if clicked_subject_id in selected_subjects:
            selected_subjects.remove(clicked_subject_id)
        else:
            selected_subjects.add(clicked_subject_id)
        
        await callback.message.edit_reply_markup(
            reply_markup=change_subjects_keyboard(selected_subjects, user_id)
        )
        await callback.answer()

    async def process_subjects_save(self,callback: CallbackQuery):
        user_id = int(callback.data.split(":")[-1])
        user = await self.user_worker.get_user(user_id)
        
        selected_subjects = []
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data.startswith("changed_subject_tgl:") and "✅" in btn.text:
                    subject_id = btn.callback_data.split(":")[-1]
                    selected_subjects.append(subject_id)
        
        if not selected_subjects:
            await callback.answer("Нужно дать пользователю хотя бы один предмет ", show_alert=True)
            return
        
        subjects_str = ",".join(selected_subjects)
        
        success = await self.user_worker.update_user(
            user_id=user_id,
            student_subjects=subjects_str
        )
        
        if success:
            subject_names = []
            for subj_id in selected_subjects:
                subject_names.append(subjects.get(subj_id, f"Предмет {subj_id}"))
            
            await callback.message.delete()
            await callback.message.answer(
                f"✅ Предметы успешно Изменены!\n\n"
                f"Пользователь: {user['user_name']}\n"
                f"User ID: {user_id}\n"
                f"Предметы: {', '.join(subject_names)}\n"
                f"ID предметов: {subjects_str}"
            )
        else:
            await callback.answer("Ошибка при сохранении предметов!", show_alert=True)
        
        await callback.answer()