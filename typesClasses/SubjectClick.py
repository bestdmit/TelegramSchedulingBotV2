from typing import Optional
from aiogram.filters.callback_data import CallbackData

class SubjectClick(CallbackData, prefix="subject"):
    """Callback для выбора предмета при бронировании"""
    subject_id: str
    action: str = "select"