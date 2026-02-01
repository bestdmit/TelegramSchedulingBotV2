from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import roles, subjects
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

#клавиатура и главное меню
def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новая кнопка")],
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