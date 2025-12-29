import asyncpg
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection_string = "postgresql://shedull_user:ShedullBot123!@localhost:5433/ShedullBot"
        self.pool = None
    
    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.connection_string)
            logger.info("✅ PostgreSQL подключена")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {e}")
            raise
    
    async def close(self):
        if self.pool:
            await self.pool.close()
    
    async def save_user(self, user_id: int, user_name: str, roles: str = "", teacher_subjects: str = "") -> bool:
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, user_name, roles, teacher_subjects)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        user_name = $2,
                        roles = $3,
                        teacher_subjects = $4,
                        updated_at = CURRENT_TIMESTAMP
                """, user_id, user_name, roles, teacher_subjects)
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения пользователя: {e}")
            return False
    
    async def get_user(self, user_id: int):
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1",
                    user_id
                )
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя: {e}")
            return None
    
    async def get_user_roles(self, user_id: int):
        user = await self.get_user(user_id)
        if user and user.get('roles'):
            return [r.strip() for r in user['roles'].split(',') if r.strip()]
        return []
    
    async def find_users_by_name(self, search_query: str):
        try:
            async with self.pool.acquire() as conn:
                users = await conn.fetch(
                    "SELECT user_id, user_name, roles, teacher_subjects FROM users WHERE user_name ILIKE $1 ORDER BY user_name LIMIT 20",
                    f"%{search_query}%"
                )
                return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"❌ Ошибка поиска пользователей: {e}")
            return []
    
    async def add_role_with_subjects(self, user_id: int, role: str, subjects: list):
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            current_roles = await self.get_user_roles(user_id)
            new_roles = set(current_roles)
            new_roles.add(role)
            
            subjects_str = ','.join(subjects)
            user_name = user.get('user_name', '')
            
            await self.save_user(user_id, user_name, ','.join(new_roles), subjects_str)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка добавления роли: {e}")
            return False

db = Database()