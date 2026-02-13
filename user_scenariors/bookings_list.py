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
from datetime import date, datetime
from typing import Optional, Dict, Any

class BookingsListService:
    '''Сервис для управления списком бронирований'''
    def __init__(self, 
                 user_worker: UsersDataBaseWorker, 
                 booking_worker: BookingsDataBaseWorker):
        self.user_worker = user_worker
        self.booking_worker = booking_worker
    
    async def Show_bookings(self,message:Message,
                             user_id: int = None):
        """Показать бронирования"""
        target_user_id = user_id or message.from_user.id
        bookings = await self.booking_worker.get_bookings_by_id(target_user_id)
        builder = InlineKeyboardBuilder()

        for booking in bookings:
            builder.button(
                text=f"📅 {booking['event_date']} - {booking['event_time']}",
                callback_data=f"booking_info_{booking['booking_id']}"
            )
        builder.adjust(1)
        text = f"Выберите бронирование\nКоличество: {len(bookings)}"
        try:
            await message.edit_text(text=text, reply_markup=builder.as_markup())
        except:
            await message.answer(text=text, reply_markup=builder.as_markup())
    
    async def booking_info(self,callback:CallbackQuery,
                           booking_worker:BookingsDataBaseWorker):
        booking_id = int(callback.data.split("_")[-1])
        booking = await booking_worker.get_booking_by_id(booking_id=booking_id)

        res = (f"Дата бронирования: {booking["event_date"]}\n"+
                f"Ваша роль при бронировании: {booking["user_role"]}\n"+
                f"Время бронирования: {booking["event_time"]}")
        
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Удалить бронирование",
            callback_data=f"delete_booking_{booking_id}"
        )
        await  callback.message.answer(
            text=res,
            reply_markup=builder.as_markup()
        )
    
    async def delete_booking_confirmation(self, callback: CallbackQuery):
        """Этап 1: Запрос подтверждения удаления"""
        booking_id = int(callback.data.split("_")[-1])
        booking = await self.booking_worker.get_booking_by_id(booking_id)

        if not booking:
            await callback.answer("Бронирование не найдено", show_alert=True)
            return

        res = (f"❓ **Вы точно хотите удалить это бронирование?**\n\n"
               f"📅 Дата: {booking['event_date']}\n"
               f"⏰ Время: {booking['event_time']}")
        
        builder = InlineKeyboardBuilder()
        builder.button(
            text="✅ Да, удалить", 
            callback_data=f"confirm_delete_{booking_id}"
        )
        builder.button(
            text="❌ Нет, оставить", 
            callback_data=f"cancel_delete"
        )
        builder.adjust(1)

        await callback.message.edit_text(text=res, reply_markup=builder.as_markup())

    async def confirm_delete(self, callback: CallbackQuery):
        """Этап 2: Окончательное удаление из БД"""
        booking_id = int(callback.data.split("_")[-1])
        
        success = await self.booking_worker.delete_booking(booking_id)
        
        if success:
            await callback.answer("Бронирование успешно удалено", show_alert=True)
            await self.Show_bookings(callback.message)
            await callback.message.delete()
        else:
            await callback.answer("Ошибка при удалении", show_alert=True)

    async def cancel_delete(self, callback: CallbackQuery):
        """Этап 3: Отмена удаления"""
        await callback.answer("Удаление отменено")
        await self.Show_bookings(callback.message)
        await callback.message.delete()

