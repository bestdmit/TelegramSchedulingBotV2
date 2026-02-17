from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from config import admin_ids
async def set_special_menu(bot: Bot):
    admin_commands = [
        BotCommand(command="show",description="Не обработанные юзеры"),
        BotCommand(command="all_users",description="Все пользователи"),
        BotCommand(command="parent_hub",description="Родители")
    ]
    for user_id in admin_ids:
        try:
            await bot.set_my_commands(
                commands=admin_commands,
                scope=BotCommandScopeChat(chat_id=user_id)
            )
        except Exception as e:
            print(f"Не удалось установить команды для {user_id}: {e}")