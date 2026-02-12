from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
from states.BookingStates import BookingStates
from keyboards import create_calendar_keyboard, create_time_keyboard
from typesClasses.CalendarClick import CalendarClick
from typesClasses.TimeClick import TimeClick, get_day_info
import datetime
from datetime import date
from typing import Optional, Dict, Any

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
    
    async def handle_teacher_booking(self, callback: CallbackQuery) -> None:
        """Обрабатывает выбор режима преподавателя"""
        now = datetime.datetime.now()
        await callback.message.answer(
            text="Вы выбрали режим преподавателя\nВыберите дату для записи:",
            reply_markup=create_calendar_keyboard(now.year, now.month)
        )
        await callback.answer()
    
    async def handle_student_booking(self, callback: CallbackQuery) -> None:
        """Обрабатывает выбор режима ученика"""
        await callback.message.answer("Вы выбрали режим ученика")
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
                                    state: FSMContext) -> None:
        """Обрабатывает выбор времени"""
        if callback_data.action == "back":
            today = datetime.now()
            await callback.message.edit_text(
                "Выберите дату для записи: ",
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
            
            user_data = await userWorker.get_user(callback.from_user.id)
            date_str = f"{callback_data.day:02d}.{callback_data.month:02d}.{callback_data.year}"
            
            builder = InlineKeyboardBuilder()
            builder.button(text="✅ Да, записать", callback_data="confirm_booking")
            builder.button(text="❌ Отмена", callback_data="booking_cancel")
            
            await callback.message.edit_text(
                f"📍 Подтверждение бронирования:\n\n"
                f"Дата: {date_str}\n"
                f"Интервал: {start} — {end}\n"
                f"Имя: {user_data.get('user_name')}\n\n"
                f"Бронируем этот промежуток?",
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
        
        user_data = await self.user_worker.get_user(callback.from_user.id)
        event_date = data.get("event_date")
        
        if not event_date:
            await callback.answer("❌ Дата не выбрана", show_alert=True)
            return
        
        date_str = event_date.strftime("%d.%m.%Y")
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Подтвердить", callback_data="confirm_booking")
        builder.button(text="❌ Отмена", callback_data="booking_cancel")
        builder.adjust(2)
        
        await callback.message.edit_text(
            f"📍 <b>Подтверждение бронирования:</b>\n\n"
            f"📅 Дата: {date_str}\n"
            f"⏰ Время: {start} — {end}\n"
            f"👤 Имя: {user_data.get('user_name', 'Не указано')}\n\n"
            f"Подтверждаете бронирование?",
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
    
    async def confirm_booking(self, callback: CallbackQuery, state: FSMContext, userWorker: UsersDataBaseWorker) -> None:
        """Подтверждает и сохраняет бронирование в БД"""
        from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
        bookingWorker = BookingsDataBaseWorker()
        
        try:
            await bookingWorker.connect()
            print("Подключение к БД bookings установлено")
        except Exception as e:
            print(f"Ошибка подключения к БД bookings: {e}")
            await callback.answer("Ошибка подключения к базе данных bookingd", show_alert=True)
            return
        data = await state.get_data()
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")
        if not start_time_str or not end_time_str:
            await callback.answer("Не выбрано время", show_alert = True)
            return
        event_date = data.get("event_date")
        if not event_date:
            event_date = datetime.data.today()
        
        user_id = callback.from_user.id
        user_data = await userWorker.get_user(user_id)
        if not user_data:
            await callback.answer("Пользователь не найден", show_alert = True)
            return 
        
        time_range = f"{start_time_str}-{end_time_str}"
        roles = user_data.get("roles", "")
        user_role = "teacher" if "teacher" in roles else "student" if "student" in roles else "unknown"
        
        success = await bookingWorker.add_booking(
            user_id=user_id,
            user_role=user_role,
            subjects=user_data.get("subjects", ""),
            event_date=event_date,
            event_time=time_range  
        )
        
        if success:
            formatted_date = event_date.strftime("%d.%m.%Y")
            
            await callback.message.edit_text(
                f"Бронирование сохранено в БД!\n\n"
                f"Дата: {formatted_date}\n"
                f"Время: {time_range}\n"
                f"Роль: {user_role}\n"
                f"Предметы: {user_data.get('subjects', '')}"
            )
        else:
            await callback.answer("Ошибка сохранения в БД", show_alert=True)
        
        await callback.answer()
        await state.clear()