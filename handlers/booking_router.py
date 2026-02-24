from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
from database_workers.database_worker_for_parents import ParentsDataBaseWorker
from user_scenariors.booking_factory import BookingServiceFactory
from typesClasses.CalendarClick import CalendarClick
from typesClasses.TimeClick import TimeClick
from aiogram.filters import Command
booking_router = Router()

@booking_router.message(F.text == "Забронировать время")
async def handle_book_time(message: Message, 
                          state: FSMContext, 
                          userWorker: UsersDataBaseWorker,
                          bookingWorker:BookingsDataBaseWorker):
    """Обработчик начала бронирования"""
    
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    
    result = await service.start_booking(message, state)
    
    if not result["success"]:
        await message.answer(result["message"])
        return
    
    await message.answer(result["message"])
    await service.show_booking_options(message, result["user_data"])


@booking_router.callback_query(F.data == "booking_teacher")
async def handle_teacher_booking(callback: CallbackQuery, 
                                userWorker: UsersDataBaseWorker,
                                state: FSMContext,
                                bookingWorker:BookingsDataBaseWorker):
    """Обработчик выбора режима преподавателя"""
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.handle_teacher_booking(callback, state)


@booking_router.callback_query(F.data == "booking_student")
async def handle_student_booking(callback: CallbackQuery,
                                userWorker: UsersDataBaseWorker,
                                state: FSMContext,
                                bookingWorker:BookingsDataBaseWorker,
                                parentsWorker: ParentsDataBaseWorker):
    """Обработчик выбора режима ученика"""
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    # Если это родитель — предложим выбрать ребёнка
    user_data = await userWorker.get_user(callback.from_user.id)
    roles = user_data.get("roles", "") if user_data else ""
    if roles and "parent" in roles:
        childrens = await parentsWorker.get_children(callback.from_user.id)
        if not childrens:
            await callback.message.answer("У вас нет привязанных детей.")
            await callback.answer()
            return

        builder = InlineKeyboardBuilder()
        for cid in childrens:
            child = await userWorker.get_user(cid)
            name = child.get('user_name') if child else str(cid)
            builder.button(text=f"{name}", callback_data=f"booking_child_{cid}")
        builder.adjust(1)
        await callback.message.answer("Выберите ребёнка для записи:", reply_markup=builder.as_markup())
        await callback.answer()
        return

    await service.handle_student_booking(callback, state)


@booking_router.callback_query(F.data == "booking_cancel")
async def handle_booking_cancel(callback: CallbackQuery, 
                               state: FSMContext,
                               userWorker: UsersDataBaseWorker,
                               bookingWorker:BookingsDataBaseWorker):
    """Обработчик отмены бронирования"""
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.cancel_booking(callback, state)


@booking_router.callback_query(CalendarClick.filter())
async def process_calendar_selection(callback: CallbackQuery, 
                                    callback_data: CalendarClick, 
                                    state: FSMContext,
                                    userWorker: UsersDataBaseWorker,
                                    bookingWorker:BookingsDataBaseWorker):
    """Обработчик выбора даты в календаре"""
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.process_calendar_selection(callback, callback_data, state)


@booking_router.callback_query(TimeClick.filter())
async def process_time_selection(callback: CallbackQuery, 
                                callback_data: TimeClick, 
                                state: FSMContext,
                                userWorker: UsersDataBaseWorker,
                                bookingWorker:BookingsDataBaseWorker):
    """Обработчик выбора времени"""
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.process_time_selection(callback, callback_data, state,userWorker)


@booking_router.callback_query(F.data.startswith("booking_child_"))
async def handle_booking_child(callback: CallbackQuery,
                               state: FSMContext,
                               userWorker: UsersDataBaseWorker,
                               bookingWorker: BookingsDataBaseWorker):
    # Выбор ребёнка родителем для записи
    try:
        child_id = int(callback.data.split("_")[-1])
    except Exception:
        await callback.answer()
        return

    child = await userWorker.get_user(child_id)
    if not child:
        await callback.message.answer("Ребёнок не найден")
        await callback.answer()
        return

    # Сохраняем в состоянии, что запись создаётся для ребёнка
    await state.update_data(booking_user_id=child_id, booking_role="student", booking_user_name=child.get('user_name'))

    # Перейдём к выбору даты как в режиме ученика
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.handle_student_booking(callback, state)


@booking_router.callback_query(F.data == "confirm_booking")
async def handle_confirm_booking(callback: CallbackQuery, 
                                state: FSMContext,
                                userWorker: UsersDataBaseWorker,
                                bookingWorker:BookingsDataBaseWorker):
    """Обработчик подтверждения бронирования"""
    service = BookingServiceFactory.create_booking_service(userWorker, bookingWorker)
    await service.confirm_booking(callback, state,userWorker,bookingWorker)

@booking_router.message(F.text == "Мои бронирования")
@booking_router.message(Command("show_bookings"))
async def show_my_bookings(message:Message,
                           userWorker: UsersDataBaseWorker,
                           bookingWorker:BookingsDataBaseWorker):
    service = BookingServiceFactory.create_bookings_list_service(user_worker=userWorker,
                                                                 booking_worker=bookingWorker)
    await service.Show_bookings(message=message)

@booking_router.callback_query(F.data.startswith("booking_info"))
async def show_booking_info(callback:CallbackQuery,
                             userWorker: UsersDataBaseWorker,
                           bookingWorker:BookingsDataBaseWorker):
    service = BookingServiceFactory.create_bookings_list_service(user_worker=userWorker,
                                                                 booking_worker=bookingWorker)
    await service.booking_info(callback=callback,booking_worker=bookingWorker)

@booking_router.callback_query(F.data.startswith("delete_booking_"))
async def handle_delete_request(callback: CallbackQuery, userWorker, bookingWorker):
    service = BookingServiceFactory.create_bookings_list_service(userWorker, bookingWorker)
    await service.delete_booking_confirmation(callback)

@booking_router.callback_query(F.data.startswith("confirm_delete_"))
async def handle_confirm_delete(callback: CallbackQuery, userWorker, bookingWorker):
    service = BookingServiceFactory.create_bookings_list_service(userWorker, bookingWorker)
    await service.confirm_delete(callback)

@booking_router.callback_query(F.data == "cancel_delete")
async def handle_cancel_delete(callback: CallbackQuery, userWorker, bookingWorker):
    service = BookingServiceFactory.create_bookings_list_service(userWorker, bookingWorker)
    await service.cancel_delete(callback)
