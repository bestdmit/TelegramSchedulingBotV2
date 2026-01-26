from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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