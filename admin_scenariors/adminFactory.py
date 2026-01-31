from admin_scenariors.simple_user import SimpleUserServices
from database_workers.database_worker_for_users import UsersDataBaseWorker  

class AdminServicesFactory:
    """Фабрика для сервисов админа"""

    _services_cache = {}

    @classmethod
    def create_admin_service_for_simple_users(self,user_worker:UsersDataBaseWorker)->SimpleUserServices:
        worker_id = id(user_worker)
        if worker_id not in AdminServicesFactory._services_cache:
            AdminServicesFactory._services_cache[worker_id] = SimpleUserServices(user_worker)
        return AdminServicesFactory._services_cache[worker_id]
        
