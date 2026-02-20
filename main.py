from database_workers import UsersDataBaseWorker
from database_workers import BookingsDataBaseWorker
from database_workers import ParentsDataBaseWorker
import asyncio
import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os
from handlers.user_router import user_router as user_router
from handlers.admin_router import admin_router as admin_router

from commands import set_special_menu
from handlers.booking_router import booking_router
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

print("start")


async def main():
    usersdataBaseWorker = UsersDataBaseWorker()
    bookingsDatabaseWorker = BookingsDataBaseWorker()
    parentsDataBaseWorker = ParentsDataBaseWorker()
    await usersdataBaseWorker.connect()
    await usersdataBaseWorker.add_user(1,"цуоруамуцоауцо")
    await usersdataBaseWorker.add_user(2,"Кирилл")
    await bookingsDatabaseWorker.connect()
    await parentsDataBaseWorker.connect()
    dp.include_routers(admin_router,user_router,booking_router)
    dp.startup.register(set_special_menu)
    await dp.start_polling(bot,
                           userWorker=usersdataBaseWorker,
                           bookingWorker= bookingsDatabaseWorker,
                           parentsWorker=parentsDataBaseWorker)

    # # Проверка работы модуля записей
    # await bookingsDatabaseworker.connect()
    # await bookingsDatabaseworker.add_booking(user_id=1,
    #                                    user_role="teacher",
    #                                    subjects="math",
    #                                    event_date=datetime.date(2026,1,20),
    #                                    event_time=datetime.time(11,45),
    #                                    point_type="begin",
    #                                    time_type="fact")



    # Проверка работы модуля пользователей
    # await usersdataBaseWorker.connect()
    # await usersdataBaseWorker.check_tables()
    # await usersdataBaseWorker.add_user(1,"цуоруамуцоауцо")
    # await usersdataBaseWorker.add_user(2,"Кирилл")
    # await usersdataBaseWorker.update_user(1,"Степан","teacher,student","Math,Informatic")
    # await usersdataBaseWorker.delete_user(2)
    # print((await usersdataBaseWorker.get_user(1))["user_name"])
    # print(await usersdataBaseWorker.check_user(1))
    # await usersdataBaseWorker.print_table("users")
    await dp.start_polling(bot, userWorker=usersdataBaseWorker, bookingWorker = bookingsDatabaseWorker)
    

asyncio.run(main())