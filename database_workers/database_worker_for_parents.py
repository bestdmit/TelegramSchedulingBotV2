import os
from typing import Any, Dict, Optional,List
from dotenv import load_dotenv
import asyncio
import asyncpg
import psycopg2
import logging
import datetime
load_dotenv()
class ParentsDataBaseWorker:
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
    
    async def add_parent_child_relation(self, parent_id: int, child_id: int):
        """Добавляет связь родитель-ребенок. Если связь уже есть, ничего не делает."""
        query = """
        INSERT INTO parents (parent_id, child_id)
        VALUES ($1, $2)
        ON CONFLICT (parent_id, child_id) DO NOTHING;
        """
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(query, parent_id, child_id)
                if result == "INSERT 0 0":
                    # print("Связь уже существует")
                    return False 
                # print(f"Связь установлена: родитель {parent_id} -> ребенок {child_id}")
                return True
        except Exception as e:
            print(f"Ошибка при добавлении связи: {e}")
            return False
    
    async def get_children(self, parent_id: int) -> List[int]:
        """Возвращает список всех ID детей для данного родителя."""
        query = "SELECT child_id FROM parents WHERE parent_id = $1;"
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, parent_id)
                # Превращаем список записей в простой список ID
                return [row['child_id'] for row in rows]
        except Exception as e:
            print(f"Ошибка при получении списка детей: {e}")
            return []
        
    async def check_parent(self,parent_id:int)->bool:
        """Проверяет, есть ли у данного ID дети (является ли он родителем)"""
        query = "SELECT 1 FROM parents WHERE parent_id = $1 LIMIT 1;"
        try:
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow(query, parent_id)
                return row is not None
        except Exception as e:
            print(f"Ошибка при проверке родителя: {e}")
            return False