from typing import Optional
from aiogram.filters.callback_data import CallbackData

class BaseClick(CallbackData, prefix = "base"):
    '''(Из старого класса CalendarClick) Возможные типы: prev,next,ignore,day (это типы кнопок на календаре)'''
    action: str
    year: Optional[int] = 0
    month: Optional[int] = 0
    day: Optional[int] = 0
    hour: Optional[int] = 0
    minute: Optional[int] = 0


