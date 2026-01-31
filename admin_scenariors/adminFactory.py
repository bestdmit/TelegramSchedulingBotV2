from admin_scenariors.simple_user import SimpleUserServices
from database_workers.database_worker_for_users import UsersDataBaseWorker  
from admin_scenariors.show_all_users import AllUserServices

class AdminServicesFactory:
    """Фабрика для сервисов админа"""

    _simple_users_cache = {}
    _all_users_cache = {}

    @classmethod
    def create_admin_service_for_simple_users(cls, user_worker: UsersDataBaseWorker) -> SimpleUserServices:
        """Создает или возвращает кэшированный сервис для работы с простыми пользователями"""
        worker_id = id(user_worker)
        if worker_id not in cls._simple_users_cache:
            cls._simple_users_cache[worker_id] = SimpleUserServices(user_worker)
        return cls._simple_users_cache[worker_id]
    
    @classmethod
    def create_admin_service_for_all_users(cls, user_worker: UsersDataBaseWorker) -> AllUserServices:
        """Создает или возвращает кэшированный сервис для работы со всеми пользователями"""
        worker_id = id(user_worker)
        if worker_id not in cls._all_users_cache:
            cls._all_users_cache[worker_id] = AllUserServices(user_worker)
        return cls._all_users_cache[worker_id]