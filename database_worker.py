import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import asyncio
import asyncpg
load_dotenv()
class DataBaseWorker:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if self.connection_string:
            print("Используется URL:"+self.connection_string)
        else:
            print("База не подключена")

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.connection_string)
            print("Успешное подключение БД")
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")

    async def check_tables(self):
        try:
            async with self.pool.acquire() as conn:
                tables = await conn.fetch("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        AND table_name IN ('users')
                    """)
            print(tables)
        except Exception as e:
            print(e)
    
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

    
