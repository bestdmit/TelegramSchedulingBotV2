from typing import Optional
from aiogram.filters.callback_data import CallbackData


class CalendarClick(CallbackData, prefix="mycal"):
    '''Возможные типы: prev,next,ignore,day (это типы кнопок на календаре)'''
    action: str
    year: int
    month: int
    day: Optional[int] = 0 