from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
from user_scenariors.booking_factory import BookingServiceFactory
from typesClasses.CalendarClick import CalendarClick
from typesClasses.TimeClick import TimeClick
import datetime
from datetime import date, time, datetime as dt
booking_router = Router()

@booking_router.message(F.text == "Забронировать время")
async def handle_book_time(message: Message, 
                          state: FSMContext, 
                          userWorker: UsersDataBaseWorker):
    """Обработчик начала бронирования"""
    bookingWorker = BookingsDataBaseWorker()
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    
    result = await service.start_booking(message, state)
    
    if not result["success"]:
        await message.answer(result["message"])
        return
    
    await message.answer(result["message"])
    await service.show_booking_options(message, result["user_data"])


@booking_router.callback_query(F.data == "booking_teacher")
async def handle_teacher_booking(callback: CallbackQuery, 
                                userWorker: UsersDataBaseWorker):
    """Обработчик выбора режима преподавателя"""
    bookingWorker = BookingsDataBaseWorker()
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.handle_teacher_booking(callback)


@booking_router.callback_query(F.data == "booking_student")
async def handle_student_booking(callback: CallbackQuery,
                                userWorker: UsersDataBaseWorker):
    """Обработчик выбора режима ученика"""
    bookingWorker = BookingsDataBaseWorker()
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.handle_student_booking(callback)


@booking_router.callback_query(F.data == "booking_cancel")
async def handle_booking_cancel(callback: CallbackQuery, 
                               state: FSMContext,
                               userWorker: UsersDataBaseWorker):
    """Обработчик отмены бронирования"""
    bookingWorker = BookingsDataBaseWorker()
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.cancel_booking(callback, state)


@booking_router.callback_query(CalendarClick.filter())
async def process_calendar_selection(callback: CallbackQuery, 
                                    callback_data: CalendarClick, 
                                    state: FSMContext,
                                    userWorker: UsersDataBaseWorker):
    """Обработчик выбора даты в календаре"""
    bookingWorker = BookingsDataBaseWorker()
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.process_calendar_selection(callback, callback_data, state)


@booking_router.callback_query(TimeClick.filter())
async def process_time_selection(callback: CallbackQuery, 
                                callback_data: TimeClick, 
                                state: FSMContext,
                                userWorker: UsersDataBaseWorker):
    """Обработчик выбора времени"""
    bookingWorker = BookingsDataBaseWorker()
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.process_time_selection(callback, callback_data, state)


@booking_router.callback_query(F.data == "confirm_booking")
async def handle_confirm_booking(callback: CallbackQuery, 
                                state: FSMContext,
                                userWorker: UsersDataBaseWorker):
    """Обработчик подтверждения бронирования"""
    bookingWorker = BookingsDataBaseWorker()
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.confirm_booking(callback, state,userWorker)