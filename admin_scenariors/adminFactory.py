from admin_scenariors.simple_user import SimpleUserServices
from database_workers.database_worker_for_users import UsersDataBaseWorker  
from database_workers.database_worker_for_parents import ParentsDataBaseWorker # Импортируем воркер
from admin_scenariors.show_all_users import AllUserServices
from admin_scenariors.parent_user import ParentUserServices # Импортируем ваш новый класс

class AdminServicesFactory:
    """Фабрика для сервисов админа"""

    _simple_users_cache = {}
    _all_users_cache = {}
    _parent_users_cache = {} # Кэш для сервиса родителей

    @classmethod
    def create_admin_service_for_simple_users(cls, user_worker: UsersDataBaseWorker) -> SimpleUserServices:
        worker_id = id(user_worker)
        if worker_id not in cls._simple_users_cache:
            cls._simple_users_cache[worker_id] = SimpleUserServices(user_worker)
        return cls._simple_users_cache[worker_id]
    
    @classmethod
    def create_admin_service_for_all_users(cls, user_worker: UsersDataBaseWorker) -> AllUserServices:
        worker_id = id(user_worker)
        if worker_id not in cls._all_users_cache:
            cls._all_users_cache[worker_id] = AllUserServices(user_worker)
        return cls._all_users_cache[worker_id]

    @classmethod
    def create_admin_service_for_parent_users(cls, user_worker: UsersDataBaseWorker, parent_worker: ParentsDataBaseWorker) -> ParentUserServices:
        """Создает или возвращает кэшированный сервис для работы с родителями"""
        cache_key = (id(user_worker), id(parent_worker))
        if cache_key not in cls._parent_users_cache:
            cls._parent_users_cache[cache_key] = ParentUserServices(user_worker, parent_worker)
        return cls._parent_users_cache[cache_key]
