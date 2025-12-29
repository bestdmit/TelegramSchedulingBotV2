from database_worker import DataBaseWorker
import asyncio

print("start")


async def main():
    dataBaseWorker = DataBaseWorker()
    await dataBaseWorker.connect()
    await dataBaseWorker.check_tables()


asyncio.run(main())