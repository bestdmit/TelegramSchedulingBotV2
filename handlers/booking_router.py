from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from booking_manager import start_booking_for_user
# from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
import datetime  
from datetime import date, time, datetime as dt 
from keyboards import create_calendar_keyboard, create_time_keyboard
from typesClasses.CalendarClick import CalendarClick
from typesClasses.TimeClick import TimeClick, get_day_info
from aiogram.fsm.state import StatesGroup, State
from states.BookingStates import BookingStates
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
booking_router = Router()

@booking_router.message(F.text == "Забронировать время")
async def handle_book_time(message: Message, state: FSMContext, userWorker):
    from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
    bookingWorker = BookingsDataBaseWorker()
    result = await start_booking_for_user(message = message, state = state, user_worker = userWorker, booking_worker = bookingWorker)
    if not result["success"]:
        await message.answer(result["message"])
        return
    
    await message.answer(result["message"])
    await show_booking_options(message, result["user_data"])

async def show_booking_options(message: Message, user_data: dict):
    builder = InlineKeyboardBuilder()
    roles = user_data.get("roles", "")
    user_roles = [role.strip() for role in roles.split(',')]
    if 'teacher' in user_roles:
        builder.button(
            text = "Записаться как преподаватель",
            callback_data="booking_teacher"
        )
    if 'student' in user_roles:
        builder.button(
            text = "Записаться как ученик",
            callback_data="booking_student"
        )
    builder.button(
        text = "Отмена",
        callback_data="booking_cancel"
    )
    builder.adjust(1)
    await message.answer(
        "Выберите тип бронирования: ",
        reply_markup=builder.as_markup()
    )


@booking_router.callback_query(F.data == "booking_teacher")
async def handle_teacher_booking(callback: CallbackQuery):
    await callback.message.answer(
        text="Вы выбрали режим преподавателя",
        reply_markup= create_calendar_keyboard(datetime.datetime.now().year,datetime.datetime.now().month)
        )

@booking_router.callback_query(F.data == "booking_student")
async def handle_student_booking(callback: CallbackQuery):
    await callback.message.answer("Вы выбрали режим ученика")
    await callback.answer()

@booking_router.callback_query(F.data == "booking_cancel")
async def handle_booking_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Бронирование отменено")
    await callback.answer()

@booking_router.callback_query(CalendarClick.filter())
async def process_calendar_selection(callback: CallbackQuery, callback_data: CalendarClick, state: FSMContext):
    if callback_data.action == "ignore":
        await callback.answer()
        return
    elif callback_data.action in ["prev","next"]:
        await callback.message.edit_reply_markup(
            reply_markup=create_calendar_keyboard(callback_data.year,callback_data.month)
        )
    elif callback_data.action == "day":
        selected_date = date(callback_data.year, callback_data.month, callback_data.day)
        await state.update_data(event_date=selected_date)
        day_info = get_day_info(selected_date)
        await callback.message.edit_text(
            f"{day_info["day_name"]}, {callback_data.day:02d}.{callback_data.month:02d}.{callback_data.year}\n"
            f"Время работы: {day_info["hours_str"]}\n"
            f"Выберите время: ",
            reply_markup=create_time_keyboard(selected_date)

        )
        await callback.answer()
    # else:
    #     date_str = f"{callback_data.day:02d}.{callback_data.month:02d}.{callback_data.year}"
    #     await callback.message.answer(f"Вы выбрали дату: {date_str}")
    #     await callback.answer()

@booking_router.callback_query(TimeClick.filter())
async def process_time_selection(callback: CallbackQuery, callback_data: TimeClick, state: FSMContext, userWorker):
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

@booking_router.callback_query(F.data == "confirm_booking")
async def handle_confirm_booking(callback: CallbackQuery, state: FSMContext, userWorker: UsersDataBaseWorker):
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