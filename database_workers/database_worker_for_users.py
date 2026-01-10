import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import asyncio
import asyncpg
import psycopg2
import logging
import datetime
load_dotenv()
class UsersDataBaseWorker:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if self.connection_string:
            print("Используется URL:"+self.connection_string)
        else:
            print("База не подключена")

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.connection_string)
            print("Успешное подключение к БД через asyncpg")
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise

    async def check_tables(self):
        """Проверяет существующие таблицы"""
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return
            async with self.pool.acquire() as conn:
                tables = await conn.fetch("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
            print("Таблицы в бд:",tables)
        except Exception as e:
            print(f"Ошибка проверки таблиц: {e}")
    
    async def print_table(self,tableName:str):
        """Показывает содержимое таблицы"""
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('SELECT * FROM users')
                print(f'Строки в таблице {tableName}: ',rows)
        except Exception as e:
            print(f"Проблема с демонстрацией таблицы {tableName}")
    
    async def add_user(self,user_id:int,user_name:str,
                       roles:str = None,teacher_subjects:str = None,
                       created_at:datetime = None,updated_at:datetime = None)->bool:
        """Добавляет пользователя"""
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return
            async with self.pool.acquire() as conn:
                if roles == None:
                    query = """
                        INSERT INTO users (user_id, user_name) 
                        VALUES ($1, $2)
                        ON CONFLICT (user_id) DO NOTHING;
                    """
                    await conn.execute(query, user_id, user_name)
                elif ("teacher" in roles.lower().split()) and (teacher_subjects != None):
                    query = """
                        INSERT INTO users (user_id, user_name, roles, teacher_subjects) 
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (user_id) DO NOTHING;
                    """
                    await conn.execute(query,user_id,user_name,roles,teacher_subjects)
                else:
                    query = """
                        INSERT INTO users (user_id, user_name, roles) 
                        VALUES ($1, $2, $3)
                        ON CONFLICT (user_id) DO NOTHING;
                    """
                    await conn.execute(query,user_id,user_name,roles)
                
                print(f"Пользователь {user_name} успешно добавлен")
                return True
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return False
            
    async def update_user(self,user_id:int,user_name:str = None,
                       roles:str = None,teacher_subjects:str = None,
                       created_at:datetime = None,updated_at:datetime = None)->bool:
        """Обновляет данные пользователя(кроме id)"""
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return 
            updates = []
            values = []
            counter = 1

            if user_name is not None:
                updates.append(f"user_name = ${counter}")
                values.append(user_name)
                counter +=1
            
            if roles is not None:
                updates.append(f"roles = ${counter}")
                values.append(roles)
                counter += 1

            if teacher_subjects is not None:
                updates.append(f"teacher_subjects = ${counter}")
                values.append(teacher_subjects)
                counter += 1
            
            if not updates:
                print("Нет данных для обновления")
                return False
            
            values.append(user_id)
            where_clause = f"${counter}"
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = {where_clause}"

            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *values)
                if result == "UPDATE 1":
                    print(f"Данные пользователя {user_id} обновлены")
                    return True
                else:
                    print(f"Пользователь с ID {user_id} не найден")
                    return False
        except Exception as e:
            print(f"Ошибка при обновлении пользователя: {e}")
            return False
    
    async def delete_user(self,user_id:int)->bool:
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return 
            
            async with self.pool.acquire() as conn:
                query = "DELETE FROM users WHERE user_id = $1"
                await conn.execute(query,user_id)
                print(f"Пользователь {user_id} успешно удален")
        except Exception as e:
            print(f"Ошиюка удаления пользователя: {e}")
            
    async def check_user(self,user_id:int)->bool:
        """Проверяет записан ли уже пользователь"""
        try:
            if not self.pool:
                print("Нет подключения к БД")
                return 
            get = await self.get_user(user_id)
            return (get is not None)
        except Exception as e:
            print(f"Ошибка проверки существования пользователя: {e}")
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает пользователя по ID"""
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1", user_id
                )
                return dict(user) if user else None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    
    

    
