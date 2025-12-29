import os
from dotenv import load_dotenv
load_dotenv()
class DataBaseWorker:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if self.connection_string:
            print("База подключена")
        else:
            print("База не подключена")