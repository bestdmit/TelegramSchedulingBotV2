from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton
from config import roles, subjects
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
import calendar
from datetime import datetime
from typesClasses.CalendarClick import CalendarClick
#клавиатура и главное меню
def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Забронировать время")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

#меню без ролей
def get_no_roles_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Обратиться к администратору")],
            [KeyboardButton(text="Проверить наличие ролей")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_admin_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[KeyboardButton(text="Добавить/Изменить предметы")],resize_keyboard=True
    )
    return True

#Клавиатура получения ролей?
def get_roles_keyboard(selected_roles:set,selected_user_id:int):
    builder = InlineKeyboardBuilder()

    for role in roles:
        label = f"{role}"
        if role in selected_roles:
            label = "✅ "+label
        builder.button(
            text = label,
            callback_data=f"role_tgl:{selected_user_id}:{role}"
        )
    builder.adjust(2)

    builder.row(types.InlineKeyboardButton(
        text="Применить ✅", 
        callback_data=f"role_save:{selected_user_id}"
        )
    )
    return builder.as_markup()

#Клавиатура получения предметов
def get_subjects_keyboard(selected_subjects: set, user_id: int):
    builder = InlineKeyboardBuilder()
    
    for subject_id, subject_name in subjects.items():
        label = f"{subject_name}"
        if subject_id in selected_subjects:
            label = "✅ " + label
        
        builder.button(
            text=label,
            callback_data=f"subject_tgl:{user_id}:{subject_id}"
        )
    
    builder.adjust(2)
    
    builder.row(types.InlineKeyboardButton(
        text="✅ Сохранить предметы",
        callback_data=f"subjects_save:{user_id}"
    ))
    
    return builder.as_markup()

def create_calendar_keyboard(year:int,month:int):
    now = datetime.now()
    builder = InlineKeyboardBuilder()

    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
              "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    builder.row(InlineKeyboardButton(
        text=months[month-1],
        callback_data=CalendarClick(action="ignore",year=year,month=month).pack()
    ))

    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    builder.row(*[
        InlineKeyboardButton(text=day,callback_data="ignore") for day in week_days
    ])

    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row_buttons = []
        for day in week:
            if day == 0:
                    row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                if datetime(year,month,day).date() < now.date():
                    row_buttons.append(
                        InlineKeyboardButton(text=" ",callback_data="ignore")
                    )
                else:
                    row_buttons.append(
                        InlineKeyboardButton(text=str(day),
                                             callback_data=CalendarClick(
                                                 action="day",year=year,month=month,
                                                 day=day
                                             ).pack())
                    )
        builder.row(*row_buttons)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    builder.row(
        InlineKeyboardButton(text="<",callback_data=CalendarClick(action="prev",
                                                                  year=prev_year,
                                                                  month=prev_month).pack()),
        InlineKeyboardButton(text=">",callback_data=CalendarClick(action="next",
                                                                  year=next_year,
                                                                  month=next_month).pack())
    )

    return builder.as_markup()

