from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_workers.database_worker_for_parents import ParentsDataBaseWorker
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
from states.BookingStates import BookingStates
from keyboards import create_calendar_keyboard, create_time_keyboard, create_subject_selection_keyboard
from typesClasses.CalendarClick import CalendarClick
from typesClasses.TimeClick import TimeClick, get_day_info
from typesClasses.SubjectClick import SubjectClick
import datetime
from datetime import date, datetime
from typing import Optional, Dict, Any
from config import rolesRU, subjects
class BookingService:
    """Сервис для управления бронированием времени"""
    
    def __init__(self, 
                 user_worker: UsersDataBaseWorker, 
                 booking_worker: BookingsDataBaseWorker):
        self.user_worker = user_worker
        self.booking_worker = booking_worker
    
    async def start_booking(self, message: Message, state: FSMContext) -> Dict[str, Any]:
        """Начинает процесс бронирования для пользователя"""
        user_data = await self.user_worker.get_user(message.from_user.id)
        
        if not user_data:
            return {
                "success": False,
                "message": "Вы не зарегистрированы в системе",
                "user_data": None
            }
        
        roles_str = user_data.get("roles", "")
        if not roles_str:
            # Если у пользователя нет ролей в users, но он является родителем
            # (связан с детьми через таблицу parents), позволяем начать бронирование
            parent_worker = ParentsDataBaseWorker()
            try:
                await parent_worker.connect()
                is_parent = await parent_worker.check_parent(message.from_user.id)
            except Exception:
                is_parent = False

            if not is_parent:
                return {
                    "success": False,
                    "message": "У вас нет назначенных ролей",
                    "user_data": user_data
                }
        
        return {
            "success": True,
            "message": "Начинаем бронирование",
            "user_data": user_data
        }
    
    async def show_booking_options(self, message: Message, user_data: dict) -> None:
        """Показывает опции бронирования в зависимости от роли пользователя"""
        builder = InlineKeyboardBuilder()
        roles = user_data.get("roles", "")
        user_roles = [role.strip() for role in roles.split(',')] if roles else []
        parent_worker = ParentsDataBaseWorker()
        await parent_worker.connect()
        if 'teacher' in user_roles:
            builder.button(
                text="Записаться как преподаватель",
                callback_data="booking_teacher"
            )
        if 'student' in user_roles:
            builder.button(
                text="Записаться как ученик",
                callback_data="booking_student"
            )
        if (await parent_worker.check_parent(message.from_user.id)):
            builder.button(
                text="Записать ребёнка",
                callback_data="booking_child_list"
            )
        
        if builder.buttons:
            builder.button(
                text="Отмена",
                callback_data="booking_cancel"
            )
            builder.adjust(1)
            
            await message.answer(
                "Выберите тип бронирования:",
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer("У вас нет ролей для бронирования")
    
    async def handle_teacher_booking(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Обрабатывает выбор режима преподавателя"""
        await state.update_data(booking_role = "teacher")
        await callback.message.delete() 
        today = datetime.today()
        await callback.message.answer(
            text="Вы выбрали режим преподавателя\nВыберите дату для записи:",
            reply_markup=create_calendar_keyboard(today.year, today.month)
        )
        await callback.answer()
    
    async def handle_student_booking(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Обрабатывает выбор режима ученика - теперь с выбором предмета"""
        await state.update_data(booking_role="student")
        await callback.message.delete()
        
        target_user_id = (await state.get_data()).get('booking_user_id') or callback.from_user.id
        user_data = await self.user_worker.get_user(target_user_id)
        
        if not user_data:
            await callback.message.answer("Ошибка получения данных пользователя")
            await callback.answer()
            return
        
        student_subjects_str = user_data.get("student_subjects", "")
        if not student_subjects_str:
            await callback.message.answer(
                "У вас нет назначенных предметов. Обратитесь к администратору."
            )
            await callback.answer()
            return
        
        subject_ids = [s_id.strip() for s_id in student_subjects_str.split(',') if s_id.strip()]
        
        if not subject_ids:
            await callback.message.answer(
                "У вас нет назначенных предметов. Обратитесь к администратору."
            )
            await callback.answer()
            return
        
        await callback.message.answer(
            text="Выберите предмет для записи:",
            reply_markup=create_subject_selection_keyboard(subject_ids)
        )
        await callback.answer()
    
    async def process_subject_selection(self, callback: CallbackQuery, 
                                            callback_data: SubjectClick,
                                            state: FSMContext) -> None:
        """Обрабатывает выбор предмета учеником"""
        subject_id = callback_data.subject_id
    
        await state.update_data(selected_subject=subject_id)        
        today = datetime.today()
        await callback.message.edit_text(
            text=f"Выбран предмет: {subjects.get(subject_id, subject_id)}\n\nВыберите дату для записи:",
            reply_markup=create_calendar_keyboard(today.year, today.month)
        )
        await callback.answer()
    
    async def cancel_booking(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Отменяет процесс бронирования"""
        await state.clear()
        await callback.message.answer("❌ Бронирование отменено")
        await callback.answer()
    
    async def process_calendar_selection(self, callback: CallbackQuery, 
                                        callback_data: CalendarClick, 
                                        state: FSMContext) -> None:
        """Обрабатывает выбор даты в календаре"""
        if callback_data.action == "ignore":
            await callback.answer()
            return
        
        if callback_data.action in ["prev", "next"]:
            await callback.message.edit_reply_markup(
                reply_markup=create_calendar_keyboard(callback_data.year, callback_data.month)
            )
            await callback.answer()
            return
        
        if callback_data.action == "day":
            selected_date = date(callback_data.year, callback_data.month, callback_data.day)
            await state.update_data(event_date=selected_date)
            day_info = get_day_info(selected_date)
            
            await callback.message.edit_text(
                f"📅 {day_info['day_name']}, {callback_data.day:02d}.{callback_data.month:02d}.{callback_data.year}\n"
                f"⏰ Время работы: {day_info['hours_str']}\n\n"
                f"Выберите время (можно выбрать несколько слотов):",
                reply_markup=create_time_keyboard(selected_date)
            )
            await callback.answer()
    
    async def process_time_selection(self, callback: CallbackQuery, 
                                    callback_data: TimeClick, 
                                    state: FSMContext,
                                    userWorker: UsersDataBaseWorker) -> None:
        """Обрабатывает выбор времени"""
        if callback_data.action == "back":
            # Возврат к календарю
            today = datetime.today()
            data = await state.get_data()
            booking_role = data.get("booking_role")
            
            if booking_role == "student":
                # Для ученика возвращаемся к выбору предмета
                target_user_id = data.get('booking_user_id') or callback.from_user.id
                user_data = await userWorker.get_user(target_user_id)
                student_subjects_str = user_data.get("student_subjects", "")
                subject_ids = [s_id.strip() for s_id in student_subjects_str.split(',') if s_id.strip()]
                
                await callback.message.edit_text(
                    "Выберите предмет для записи:",
                    reply_markup=create_subject_selection_keyboard(subject_ids)
                )
            else:
                # Для преподавателя возвращаемся к календарю
                await callback.message.edit_text(
                    "Выберите дату для записи:",
                    reply_markup=create_calendar_keyboard(today.year, today.month)
                )
            return

        if callback_data.action == "select":
            selected_date = date(callback_data.year, callback_data.month, callback_data.day)
            new_time = f"{callback_data.hour:02d}:{callback_data.minute:02d}"
            
            data = await state.get_data()
            start = data.get("start_time")
            end = data.get("end_time")

            # Логика переключения слотов
            if not start or (start and end):
                start, end = new_time, None
            else:
                if new_time > start:
                    end = new_time
                else:
                    start, end = new_time, None

            await state.update_data(start_time=start, end_time=end)

            await callback.message.edit_reply_markup(
                reply_markup=create_time_keyboard(selected_date, start, end)
            )

        # Обработка нажатия "Подтвердить"
        elif callback_data.action == "confirm":
            data = await state.get_data()
            start = data.get("start_time")
            end = data.get("end_time")
            
            data_state = await state.get_data()
            target_user_id = data_state.get('booking_user_id') or callback.from_user.id
            user_data = await userWorker.get_user(target_user_id)
            date_str = f"{callback_data.day:02d}.{callback_data.month:02d}.{callback_data.year}"
            
            # Получаем выбранный предмет для ученика
            selected_subject = data_state.get("selected_subject", "")
            subject_name = subjects.get(selected_subject, selected_subject) if selected_subject else "Не выбран"
            
            builder = InlineKeyboardBuilder()
            builder.button(text="✅ Да, записать", callback_data="confirm_booking")
            builder.button(text="❌ Отмена", callback_data="booking_cancel")
            
            text = (f"📍 Подтверждение бронирования:\n\n"
                   f"Дата: {date_str}\n"
                   f"Интервал: {start} — {end}\n"
                   f"Имя: {user_data.get('user_name')}\n")
            
            if selected_subject:
                text += f"Предмет: {subject_name}\n"
            
            text += f"\nБронируем этот промежуток?"
            
            await callback.message.edit_text(
                text,
                reply_markup=builder.as_markup()
            )

        await callback.answer()
    
    async def _show_confirmation(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Показывает экран подтверждения бронирования"""
        data = await state.get_data()
        start = data.get("start_time")
        end = data.get("end_time")
        
        if not start or not end:
            await callback.answer("❌ Выберите начальное и конечное время", show_alert=True)
            return
        
        data_state = await state.get_data()
        target_user_id = data_state.get('booking_user_id') or callback.from_user.id
        user_data = await self.user_worker.get_user(target_user_id)
        event_date = data.get("event_date")
        
        if not event_date:
            await callback.answer("❌ Дата не выбрана", show_alert=True)
            return
        
        date_str = event_date.strftime("%d.%m.%Y")
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Подтвердить", callback_data="confirm_booking")
        builder.button(text="❌ Отмена", callback_data="booking_cancel")
        builder.adjust(2)
        
        text = (f"📍 <b>Подтверждение бронирования:</b>\n\n"
               f"📅 Дата: {date_str}\n"
               f"⏰ Время: {start} — {end}\n"
               f"👤 Имя: {user_data.get('user_name', 'Не указано')}\n")
        
        # Добавляем информацию о предмете для ученика
        booking_role = data.get("booking_role")
        selected_subject = data.get("selected_subject")
        if booking_role == "student" and selected_subject:
            subject_name = subjects.get(selected_subject, selected_subject)
            text += f"📚 Предмет: {subject_name}\n"
        
        text += f"\nПодтверждаете бронирование?"
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
    
    async def confirm_booking(self, callback: CallbackQuery, 
                              state: FSMContext, userWorker: UsersDataBaseWorker,
                              bookingWorker: BookingsDataBaseWorker) -> None:
        """Подтверждает и сохраняет бронирование в БД"""
        from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
        from keyboards import get_main_menu
        
        try:
            await bookingWorker.connect()
            print("Подключение к БД bookings установлено")
        except Exception as e:
            print(f"Ошибка подключения к БД bookings: {e}")
            await callback.answer("Ошибка подключения к базе данных bookings", show_alert=True)
            return
        
        data = await state.get_data()
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")
        
        if not start_time_str or not end_time_str:
            await callback.answer("Не выбрано время", show_alert=True)
            return
        
        event_date = data.get("event_date")
        if not event_date:
            event_date = datetime.today()
        
        target_user_id = data.get('booking_user_id') or callback.from_user.id
        user_data = await userWorker.get_user(target_user_id)
        if not user_data:
            await callback.answer("Пользователь не найден", show_alert=True)
            return 
        
        time_range = f"{start_time_str}-{end_time_str}"
        
        data = await state.get_data()
        booking_role = data.get("booking_role")
        
        if not booking_role:
            roles = user_data.get("roles", "")
            if "teacher" in roles and "student" in roles:
                await callback.message.answer(
                    reply_markup=get_main_menu()
                )
                await state.clear()
                await callback.answer()
                return
        
        # Определяем предметы для бронирования
        subjects_for_booking = ""
        if booking_role == "teacher":
            subjects_for_booking = user_data.get("teacher_subjects", "")
        elif booking_role == "student":
            # Для ученика используем выбранный предмет
            selected_subject = data.get("selected_subject", "")
            if selected_subject:
                subjects_for_booking = selected_subject
            else:
                # Если предмет не выбран (для обратной совместимости)
                subjects_for_booking = user_data.get("student_subjects", "")
        
        success = await bookingWorker.add_booking(
            user_id=target_user_id,
            user_role=booking_role,
            subjects=subjects_for_booking,  
            event_date=event_date,
            event_time=time_range  
        )
        
        if success:
            formatted_date = event_date.strftime("%d.%m.%Y")
            
            # Формируем текст с предметами
            subject_names = []
            if subjects_for_booking:
                subject_ids = subjects_for_booking.split(',')
                for subj_id in subject_ids:
                    if subj_id.strip():
                        subject_names.append(subjects.get(subj_id.strip(), f"Предмет {subj_id}"))
            
            subjects_text = ", ".join(subject_names) if subject_names else "Не указаны"
            
            await callback.message.edit_text(
                f"✅ Бронирование сохранено!\n\n"
                f"📅 Дата: {formatted_date}\n"
                f"⏰ Время: {time_range}\n"
                f"👤 Роль: {rolesRU[booking_role]}\n"
                f"📚 Предметы: {subjects_text}"
            )
        else:
            await callback.answer("❌ Ошибка сохранения в БД", show_alert=True)
        
        await callback.answer()
        await state.clear()