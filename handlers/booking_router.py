from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from booking_manager import start_booking_for_user

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
    await callback.message.answer("Вы выбрали режим преподавателя")
    await callback.answer()

@booking_router.callback_query(F.data == "booking_student")
async def handle_student_booking(callback: CallbackQuery):
    await callback.message.answer("Вы выбрали режим ученика")
    await callback.answer()

@booking_router.callback_query(F.data == "booking_cancel")
async def handle_booking_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Бронирование отменено")
    await callback.answer()