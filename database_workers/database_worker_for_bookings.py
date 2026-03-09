import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import asyncio
import asyncpg
import logging
from datetime import date,time
from .database_worker_for_users import UsersDataBaseWorker
from config import time_types

load_dotenv()
class BookingsDataBaseWorker:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        self.pool = None
        if self.connection_string:
            print("Используется URL:"+self.connection_string)
        else:
            print("База не подключена")

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.connection_string)
            print("Успешное подключение записей к БД через asyncpg")
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise


    async def add_booking(self,user_id:int,user_role:str,
                          subjects:str,event_date:date,
                          event_time:str,
                          amount:float | None = None):
        """
        Добавление бронирования в БД
        
        :param event_date: Дата
        :type event_date: date
        :param event_time: Время
        :type event_time: time
        :param amount: Сумма оплаты/вознаграждения
        :type amount: float or None
        """
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return False
            async with self.pool.acquire() as conn:
                val = await conn.fetchval("SELECT MAX(booking_id) FROM bookings")
                new_id = (val or 0) + 1
                formatted_date = event_date.strftime("%d.%m.%Y")
                time_type = time_types["type1"]
                # пытаемся записать сумму, но старые базы могли не иметь этой колонки
                query = """
                        INSERT into bookings \
                            (booking_id,user_id,user_role,subjects,event_date,event_time,time_type,amount)\
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                        """
                try:
                    await conn.execute(
                        query,
                        new_id,
                        user_id, 
                        user_role, 
                        subjects,
                        formatted_date, 
                        event_time, 
                        time_type,
                        amount
                    )
                except Exception as e:
                    # если колонки нет, пробуем без неё
                    if 'column "amount"' in str(e).lower():
                        query2 = """
                                INSERT into bookings \
                                    (booking_id,user_id,user_role,subjects,event_date,event_time,time_type)\
                                VALUES ($1,$2,$3,$4,$5,$6,$7)
                                """
                        await conn.execute(
                            query2,
                            new_id,
                            user_id, 
                            user_role, 
                            subjects,
                            formatted_date, 
                            event_time, 
                            time_type
                        )
                    else:
                        raise
                print(f"Успешно добавлена запись для пользователя {user_id}")
                return True
        except Exception as e:
            print(f"Ошибка добавления записи: {e}")
            return False
        
    async def get_bookings_by_id(self, user_id: int) -> list[Dict[str, Any]]:
        """
        Возвращает все записи из таблицы bookings для конкретного user_id
        """
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return []
            
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM bookings WHERE user_id = $1 ORDER BY event_date, event_time"
                rows = await conn.fetch(query, user_id)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"Ошибка при получении записей пользователя {user_id}: {e}")
            return []
        
    async def get_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о конкретном бронировании по его booking_id.
        Возвращает словарь с данными или None, если запись не найдена.
        """
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return None
            
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM bookings WHERE booking_id = $1"
                row = await conn.fetchrow(query, booking_id)
                
                if row:
                    return dict(row)
                
                print(f"Запись №{booking_id} не найдена")
                return None
                
        except Exception as e:
            print(f"Ошибка при получении записи №{booking_id}: {e}")
            return None

    async def get_last_amount(self, user_id: int) -> Any:
        """Возвращает последнюю указанную сумму для пользователя или None"""
        if not self.pool:
            print("Нет подключения к БД")
            return None
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT amount FROM bookings WHERE user_id = $1 AND amount IS NOT NULL "
                    "ORDER BY booking_id DESC LIMIT 1",
                    user_id
                )
                return row["amount"] if row else None
        except Exception as e:
            # возможна ошибка, если колонки amount нет
            if 'column "amount"' in str(e).lower():
                return None
            print(f"Ошибка при получении последней суммы для пользователя {user_id}: {e}")
            return None

    async def delete_booking(self, booking_id: int) -> bool:
        """
        Удаляет запись из таблицы bookings по её ID.
        """
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return False

            async with self.pool.acquire() as conn:
                query = "DELETE FROM bookings WHERE booking_id = $1"
                result = await conn.execute(query, booking_id)
                
                if result == "DELETE 1":
                    print(f"Запись №{booking_id} успешно удалена")
                    return True
                else:
                    print(f"Запись №{booking_id} не найдена в базе данных")
                    return False

        except Exception as e:
            print(f"Ошибка при удалении записи №{booking_id}: {e}")
            return False
        