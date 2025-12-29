from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from config import is_admin
from database import db

async def generate_main_menu(user_id: int):
    roles = await db.get_user_roles(user_id)
    
    keyboard_buttons = []
    
    if not roles:
        keyboard_buttons.append([KeyboardButton(text="❓ Обратиться к администратору")])
        if is_admin(user_id):
            keyboard_buttons.append([KeyboardButton(text="➕ Добавить роль пользователю")])
        return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)
    
    if 'teacher' in roles or 'student' in roles or 'parent' in roles:
        keyboard_buttons.append([KeyboardButton(text="📅 Забронировать время")])
    
    keyboard_buttons.append([KeyboardButton(text="👤 Моя роль")])
    keyboard_buttons.append([KeyboardButton(text="ℹ️ Помощь")])
    
    if is_admin(user_id):
        keyboard_buttons.append([KeyboardButton(text="➕ Добавить роль пользователю")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)