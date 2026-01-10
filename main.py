from database_worker import DataBaseWorker
import asyncio

print("start")


async def main():
    dataBaseWorker = DataBaseWorker()
    await dataBaseWorker.connect()
    await dataBaseWorker.check_tables()
    await dataBaseWorker.add_user(1,"цуоруамуцоауцо")
    await dataBaseWorker.add_user(2,"Кирилл")
    await dataBaseWorker.update_user(1,"Степан","teacher,student","Math,Informatic")
    await dataBaseWorker.delete_user(2)
    print(await dataBaseWorker.check_user(1))
    await dataBaseWorker.print_table("users")


asyncio.run(main())