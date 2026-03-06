from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton, InlineKeyboardMarkup
from config import roles, subjects
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
import calendar
from datetime import datetime
from typesClasses.CalendarClick import CalendarClick
from typesClasses.TimeClick import TimeClick, get_working_hours_for_date
#клавиатура и главное меню
def get_main_menu(parent: bool = False) -> ReplyKeyboardMarkup:
    # Базовые кнопки, которые есть всегда
    buttons = [
        [KeyboardButton(text="Забронировать время")],
        [KeyboardButton(text="Обратиться к администратору")],
        [KeyboardButton(text="Мои бронирования")]
    ]
    
    # Добавляем кнопку только если условие истинно
    if parent:
        buttons.append([KeyboardButton(text="Мои дети")])
        
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

#меню без ролей
def get_no_roles_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Обратиться к администратору")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
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
def get_subjects_keyboard(selected_subjects: set, user_id):
    
    if (isinstance(user_id, int)):
        user_id = str(user_id)
    builder = InlineKeyboardBuilder()
    
    for subject_id, subject_name in subjects.items():
        label = f"{subject_name}"
        if subject_id in selected_subjects:
            label = "✅ " + label
        
        callback_data=f"subject_tgl:{user_id}:{subject_id}"
        builder.button(
            text=label,
            callback_data=callback_data
        )
    
    builder.adjust(2)
    
    builder.row(types.InlineKeyboardButton(
        text="✅ Сохранить предметы",
        callback_data=f"subjects_save:{user_id}"
    ))
    
    return builder.as_markup()


def change_roles_keyboard(selected_roles:set,selected_user_id:int):
    '''Клавиатура изменения ролей'''
    builder = InlineKeyboardBuilder()

    for role in roles:
        label = f"{role}"
        if role in selected_roles:
            label = "✅ "+label
        builder.button(
            text = label,
            callback_data=f"changed_role_tgl:{selected_user_id}:{role}"
        )
    builder.adjust(2)

    builder.row(types.InlineKeyboardButton(
        text="Применить ✅", 
        callback_data=f"changed_role_save:{selected_user_id}"
        )
    )
    return builder.as_markup()

def change_subjects_keyboard(selected_subjects: set, user_id: int):
    '''Клавиатура изменения предметов'''
    builder = InlineKeyboardBuilder()
    
    for subject_id, subject_name in subjects.items():
        label = f"{subject_name}"
        if subject_id in selected_subjects:
            label = "✅ " + label
        
        builder.button(
            text=label,
            callback_data=f"changed_subject_tgl:{user_id}:{subject_id}"
        )
    
    builder.adjust(2)
    
    builder.row(types.InlineKeyboardButton(
        text="✅ Сохранить предметы",
        callback_data=f"changed_subjects_save:{user_id}"
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

def create_time_keyboard(selected_date: datetime.date,start_selection: str = None, end_selection: str = None):
    builder = InlineKeyboardBuilder()
    work_hours = get_working_hours_for_date(selected_date)
    start_hour = work_hours["start_hour"]
    end_hour = work_hours["end_hour"]

    buttons = []
    current_hour = start_hour
    now = datetime.now()
    is_today = selected_date == now.date()
    
    while current_hour <= end_hour:
        for minute in [0, 15, 30, 45]:
            if current_hour == end_hour and minute > 0:
                continue
            
            if is_today:
                slot_time = datetime(now.year, now.month, now.day, current_hour, minute)
                if slot_time <= now:
                    continue
            
            time_str = f"{current_hour:02d}:{minute:02d}"
            label = time_str
            if time_str == start_selection:
                label = f"🟢 {time_str}"
            elif time_str == end_selection:
                label = f"🔴 {time_str}"
            elif start_selection and end_selection and start_selection < time_str < end_selection:
                label= f"🔹 {time_str}"

            buttons.append(InlineKeyboardButton(
                text=label,
                callback_data=TimeClick(
                    action="select",
                    hour=current_hour,
                    minute=minute,
                    year=selected_date.year,
                    month=selected_date.month,
                    day=selected_date.day
                ).pack()
            ))
        current_hour += 1

    for i in range(0, len(buttons), 4):
        builder.row(*buttons[i:i+4])
    
    if start_selection and end_selection:
        builder.row(InlineKeyboardButton(
            text="✅ Подтвердить интервал",
            callback_data="confirm_booking"
        ))
    builder.row(InlineKeyboardButton(
        text="Назад к календарю",
        callback_data=TimeClick(action="back", hour=0, minute=0).pack()
    ))
    return builder.as_markup()

def create_subject_selection_keyboard(subject_ids: list) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора предмета из списка ID предметов
    """
    from typesClasses.SubjectClick import SubjectClick
    from config import subjects
    
    builder = InlineKeyboardBuilder()
    
    for subject_id in subject_ids:
        subject_name = subjects.get(subject_id, f"Предмет {subject_id}")
        builder.button(
            text=subject_name,
            callback_data=SubjectClick(subject_id=subject_id).pack()
        )
    
    builder.adjust(1)  
    
    builder.row(types.InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="booking_cancel"
    ))
    
    return builder.as_markup()