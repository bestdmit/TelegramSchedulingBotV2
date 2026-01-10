from database_workers import UsersDataBaseWorker
from database_workers import BookingsDataBaseWorker
import asyncio
import datetime
print("start")


async def main():
    usersdataBaseWorker = UsersDataBaseWorker()
    bookingsDatabaseworker = BookingsDataBaseWorker()

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