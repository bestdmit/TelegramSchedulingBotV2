from database_workers import UsersDataBaseWorker
from database_workers import BookingsDataBaseWorker
import asyncio
import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

print("start")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет!")

async def main():
    usersdataBaseWorker = UsersDataBaseWorker()
    bookingsDatabaseworker = BookingsDataBaseWorker()

    await dp.start_polling(bot)

    # # Проверка работы модуля записей
    await bookingsDatabaseworker.connect()
    await bookingsDatabaseworker.add_booking(user_id=1,
                                       user_role="teacher",
                                       subjects="math",
                                       event_date=datetime.date(2026,1,20),
                                       event_time=datetime.time(11,45),
                                       point_type="begin",
                                       time_type="fact")



    # Проверка работы модуля пользователей
    # await usersdataBaseWorker.connect()
    # await usersdataBaseWorker.check_tables()
    # await usersdataBaseWorker.add_user(1,"цуоруамуцоауцо")
    # await usersdataBaseWorker.add_user(2,"Кирилл")
    # await usersdataBaseWorker.update_user(1,"Степан","teacher,student","Math,Informatic")
    # await usersdataBaseWorker.delete_user(2)
    # print(await usersdataBaseWorker.check_user(1))
    # await usersdataBaseWorker.print_table("users")
    
    

asyncio.run(main())