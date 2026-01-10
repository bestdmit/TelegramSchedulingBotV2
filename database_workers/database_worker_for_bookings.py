import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import asyncio
import asyncpg
import logging
from datetime import date,time
from .database_worker_for_users import UsersDataBaseWorker
load_dotenv()
class BookingsDataBaseWorker:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
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
                          event_time:time,point_type:str,
                          time_type:str):
        """
        Добавление бронирования в БД
        
        :param event_date: Дата
        :type event_date: date
        :param event_time: Время
        :type event_time: time
        :param point_type: Начало/конец
        :type point_type: str
        :param time_type: Возможность/факт/длительность
        :type time_type: str
        """
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return
            async with self.pool.acquire() as conn:
                val = await conn.fetchval("SELECT MAX(booking_id) FROM bookings")
                new_id = (val or 0) + 1
                query = """
                        INSERT into bookings (booking_id,user_id,user_role,subjects,event_date,event_time,point_type,time_type)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                        """
                await conn.execute(query,(new_id),user_id,user_role,subjects,event_date,event_time,point_type,time_type)
                print(f"Успешно добавлена запись №{new_id}")
        except Exception as e:
            print(f"Ошибка добавления записи: {e}")