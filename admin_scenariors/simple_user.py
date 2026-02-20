from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import subjects,rolesRU
from keyboards import get_subjects_keyboard, get_roles_keyboard
from aiogram import Bot
from keyboards import get_main_menu
class SimpleUserServices:
    """Работа с неполными пользователями"""

    def __init__(self,user_worker:UsersDataBaseWorker):
        self.user_worker = user_worker
    
    async def show_users_without_roles(self,message:Message):
        """Показать пользователей без прав"""
        simple_users = await self.user_worker.get_simple_users()
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
        
    async def process_simple_user_click(self,callback:CallbackQuery):
        user_id = callback.data.split("_")[-1]
        simple_user = await self.user_worker.get_user(int(user_id))
        roles = simple_user.get("roles", "")
        student_subjects = simple_user["student_subjects"]
        teacher_subjects = simple_user["teacher_subjects"]

        builder = InlineKeyboardBuilder()
        builder.button(
                text = "Добавить роль",
                callback_data=f"simple_user_give_role_{user_id}"
            )
        
        if roles and ("teacher" in roles) and (not teacher_subjects):
                builder.button(
                text = "Добавить предметы преподавателю",
                callback_data=f"teacher_give_subjects_{user_id}"
            )
        if roles and ("student" in roles) and (not student_subjects):
                builder.button(
                text = "Добавить предметы ученику",
                callback_data=f"student_give_subjects_{user_id}"
            )
            
        builder.adjust(2)
        await callback.message.delete()
        await callback.answer()

        user_info = f"Пользователь: {simple_user['user_name']}\n"
        user_info+=f"User Id: {user_id}\n"
        if roles == True:
            roles_list = roles.split(',')
            roles_readable = [rolesRU.get(role, role) for role in roles_list if role]
            user_info+=f"Роли: {", ".join(roles_readable)}\n"
        else:
            user_info+=f"Роли НЕ НАЗНАЧЕНЫ\n"
        if roles == True:
            if "teacher" in roles and teacher_subjects:
                teacher_subj_list = teacher_subj_list.split(",") if teacher_subjects else []
                teacher_names = [subjects.get(subj_id, f"Предмет") for subj_id in teacher_subj_list if subj_id]
                if teacher_names:
                    user_info += f"Предметы преподавателя: {", ".join(teacher_names)}"
            if "student" in roles and student_subjects:
                student_subj_list = student_subj_list.split(",") if student_subjects else []
                student_names = [subjects.get(subj_id, f"Предмет") for subj_id in student_subj_list if subj_id]
                if student_names:
                    user_info += f"Предметы ученика: {", ".join(student_names)}"
                
            if ("teacher" in roles and not teacher_subjects) or ("student" in roles and not student_subjects):
                user_info += "Предметы не назначены (требуется для выбранных ролей)\n"

        await callback.message.answer(
            user_info,
            reply_markup=builder.as_markup()
        )
        # if (roles and "teacher" in roles) or (roles and "student" in roles):
        #     subjects = simple_user.get("subjects", "")
        #     if subjects:
        #         subjects_names = []
        #         for Sub_Id in subjects.split(','):
        #             if Sub_Id.strip():
        #                 subjects_names.append(subjects.get(Sub_Id, f"Предмет {Sub_Id}"))
        #         user_info += f"Предметы: {', '.join(subjects_names)}\n"
        #     else:
        #         user_info+=f"Предметы не назначены\n"
        # await  callback.message.answer(
        #     user_info,
        #     reply_markup=builder.as_markup()
        #     )
        
    async def process_give_role(self,callback: CallbackQuery):
        user_id = int(callback.data.split("_")[-1])
        simple_user = await self.user_worker.get_user(user_id)
        current_roles = set()
        if simple_user and simple_user.get("roles"):
            current_roles = set(simple_user["roles"].split(','))
        await callback.message.answer(
            "Выберите роли:",
            reply_markup=get_roles_keyboard(selected_roles=current_roles,selected_user_id=user_id)
        )

    async def process_role_toggle(self,callback: CallbackQuery):
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

    async def process_role_save(self,callback: CallbackQuery, bot: Bot = None):
        user_id = int(callback.data.split(":")[-1])
        user_name = (await self.user_worker.get_user(user_id))["user_name"]
        final_roles = []
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data.startswith("role_tgl:") and "✅" in btn.text:
                    final_roles.append(btn.callback_data.split(":")[-1])

        if not final_roles:
            await callback.answer("Выберите хотя бы одну роль!", show_alert=True)
            return
        
        roles_str = ",".join(final_roles)
        roles_ru = ",".join([rolesRU[role] for role in final_roles])
        await self.user_worker.update_user(user_id,user_name, roles_str)

        await callback.message.delete()

        if bot:
            try:
                await bot.send_message(
                    chat_id= user_id,
                    text=f"Вам назначены роли: {roles_ru}\n"
                )
            except Exception as e:
                print("Не удалось отправить сообщение пользователю {user_id}: {e}")
        
        roles_needing_subjects = [r for r in final_roles if r in ["teacher", "student"]]
        if roles_needing_subjects:
            current_role = roles_needing_subjects[0]
            remaining_roles = roles_needing_subjects[1:] if len(roles_needing_subjects)>1 else []
            remaining_str = ":".join(remaining_roles) if remaining_roles else ""
            user_target = f"{user_id}:{current_role}"
            if remaining_str:
                user_target+= f":{remaining_str}"
            await callback.message.answer(
                f"Роли добавлены!\n"
                f"Пользователь: {user_name}\n"
                f"Теперь выберите предметы для роли {rolesRU[current_role]}:",
                parse_mode="Markdown",
                reply_markup=get_subjects_keyboard(
                    selected_subjects=set(),
                    user_id=user_target
                )
            )
        else:
            await callback.answer.message(
                f"Роли добавлены\n"
                f"Пользователь: {user_name}\n"
                f"Роли: {roles_str}"
            )

        await callback.answer()

    async def process_subject_toggle(self,callback: CallbackQuery):
        parts = callback.data.split(":")
        user_target_parts = parts[1:-1]
        user_target= ":".join(user_target_parts)
        clicked_subject_id = parts[-1]
        target_parts = user_target.split(':')
        user_id = int(target_parts[0])

        role = None
        remaining_roles= []
        if len(target_parts)>=2:
            role = target_parts[1]
            if len(target_parts) >= 3:
                remaining_roles = target_parts[2:]
        selected_subjects = set()
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("subject_tgl:"):
                    if "✅" in btn.text:
                        subject_id = btn.callback_data.split(":")[-1]
                        selected_subjects.add(subject_id)
        if clicked_subject_id in selected_subjects:
            selected_subjects.remove(clicked_subject_id)
        else:
            selected_subjects.add(clicked_subject_id)
        if role:
            new_user_target = f"{user_id}:{role}"
            if remaining_roles:
                new_user_target+=f":{":".join(remaining_roles)}"
        else:
            new_user_target = str(user_id)
        
        await callback.message.edit_reply_markup(
            reply_markup=get_subjects_keyboard(selected_subjects, new_user_target)
        )
        await callback.answer()



    async def process_subjects_save(self, callback: CallbackQuery, bot: Bot = None):
        parts = callback.data.split(":")
        user_target_parts = parts[1:]
        user_target = ":".join(user_target_parts)
        target_parts = user_target.split(":")
        
        if len(target_parts) >= 2:
            user_id = int(target_parts[0])
            current_role = target_parts[1]
            remaining_roles = target_parts[2:] if len(target_parts) > 2 else []
        else:
            user_id = int(target_parts[0])
            current_role = None
            remaining_roles = []
        
        user = await self.user_worker.get_user(user_id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        selected_subjects = []
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("subject_tgl:") and "✅" in btn.text:
                    subject_id = btn.callback_data.split(":")[-1]
                    selected_subjects.append(subject_id)
        
        if not selected_subjects:
            await callback.answer("Нужно выбрать хотя бы один предмет!", show_alert=True)
            return
        
        subjects_str = ",".join(selected_subjects)
        subject_names = [subjects.get(s_id, f"Предмет {s_id}") for s_id in selected_subjects]

        success = False
        if current_role == "teacher":
            success = await self.user_worker.update_user(
                user_id=user_id,
                teacher_subjects=subjects_str
            )
        elif current_role == "student":
            success = await self.user_worker.update_user(
                user_id=user_id,
                student_subjects=subjects_str
            )
        else:
            await callback.answer("Ошибка: не указана роль для предметов", show_alert=True)
            return
        
        if success:
            await callback.message.delete()
        
            if remaining_roles and remaining_roles[0]:
                next_role = remaining_roles[0]
                next_remaining = remaining_roles[1:] if len(remaining_roles) > 1 else []
                
                new_user_target = f"{user_id}:{next_role}"
                if next_remaining:
                    new_user_target += f":{':'.join(next_remaining)}"

                await callback.message.answer(
                    f"✅ Предметы для роли *{rolesRU[current_role]}* сохранены!\n\n"
                    f"Теперь выберите предметы для роли *{rolesRU[next_role]}*:",
                    parse_mode="Markdown",
                    reply_markup=get_subjects_keyboard(set(), new_user_target)
                )
                
            
            else:
                if bot:
                    try:
                        new_menu = get_main_menu()
                        
                        updated_user = await self.user_worker.get_user(user_id)
                        all_subjects = []
                        
                        if "teacher" in updated_user.get('roles', '') and updated_user.get('teacher_subjects'):
                            teacher_names = [subjects.get(s_id, f"Предмет {s_id}") 
                                        for s_id in updated_user['teacher_subjects'].split(',') if s_id]
                            all_subjects.append(f"Преподаватель: {', '.join(teacher_names)}")
                        
                        if "student" in updated_user.get('roles', '') and updated_user.get('student_subjects'):
                            student_names = [subjects.get(s_id, f"Предмет {s_id}") 
                                        for s_id in updated_user['student_subjects'].split(',') if s_id]
                            all_subjects.append(f"Ученик: {', '.join(student_names)}")
                        
                        subjects_text = "\n".join(all_subjects) if all_subjects else "Не назначены"
                        
                        await bot.send_message(
                            chat_id=user_id,
                            text=f"✅ Ваш профиль полностью настроен!\n\n"
                                f"Назначенные предметы:\n{subjects_text}",
                            reply_markup=new_menu
                        )
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                
                result_text = f"✅ Все предметы успешно добавлены!\n\n"
                result_text += f"Пользователь: {user['user_name']}\n"
                result_text += f"User ID: {user_id}\n"
                updated_user = await self.user_worker.get_user(user_id)
                all_subjects_text = []
                
                if updated_user.get('teacher_subjects'):
                    teacher_names = [subjects.get(s_id, f"Предмет {s_id}") 
                                for s_id in updated_user['teacher_subjects'].split(',') if s_id]
                    all_subjects_text.append(f"Преподаватель: {', '.join(teacher_names)}")
                
                if updated_user.get('student_subjects'):
                    student_names = [subjects.get(s_id, f"Предмет {s_id}") 
                                for s_id in updated_user['student_subjects'].split(',') if s_id]
                    all_subjects_text.append(f"Ученик: {', '.join(student_names)}")
                
                result_text += "\n".join(all_subjects_text)
                
                await callback.message.answer(result_text)
        else:
            await callback.answer("Ошибка при сохранении предметов в БД!", show_alert=True)
        
        await callback.answer()

    async def process_teacher_subjects(self, callback: CallbackQuery):
            user_id = int(callback.data.split("_")[-1])
            
            user = await self.user_worker.get_user(user_id)
            current_subjects = set()
            if user and user.get('teacher_subjects'):
                current_subjects = set(user['teacher_subjects'].split(','))
            
            user_target = f"{user_id}:teacher"
            
            await callback.message.answer(
                f"Выберите предметы для преподавателя:",
                reply_markup=get_subjects_keyboard(
                    selected_subjects=current_subjects,
                    user_id=user_target
                )
            )
            await callback.answer()


    async def process_student_subjects(self, callback: CallbackQuery):
        user_id = int(callback.data.split("_")[-1])
        
        user = await self.user_worker.get_user(user_id)
        current_subjects = set()
        if user and user.get('student_subjects'):
            current_subjects = set(user['student_subjects'].split(','))
        
        user_target = f"{user_id}:student"
        
        await callback.message.answer(
            f"Выберите предметы для ученика:",
            reply_markup=get_subjects_keyboard(
                selected_subjects=current_subjects,
                user_id=user_target
            )
        )
        await callback.answer()