from typing import Optional, Dict
from aiogram.filters.callback_data import CallbackData
from .BaseClick import BaseClick
from datetime import date, datetime


class TimeClick(BaseClick, prefix = "mytime"):
    pass

def get_working_hours_for_date(selected_date: date):
    weekday = selected_date.weekday()
    if weekday < 5:
        return {
            "start_hour": 14,
            "end_hour": 20,
            "work_day_type": "будний",
            "hours_str": "14:00 - 20:00"
        }
    else:
        return {
            "start_hour": 9,
            "end_hour": 15,
            "work_day_type": "выходной",
            "hours_str": "9:00 - 15:00"
        }

def get_day_info(selected_date: date) -> Dict[str,str]:
    day_names = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье"
    ]
    weekday = selected_date.weekday()
    work_hours = get_working_hours_for_date(selected_date)
    return {
        "day_name": day_names[weekday],
        "work_day_type": work_hours["work_day_type"],
        "hours_str": work_hours["hours_str"]
    }