from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
from database_workers.database_worker_for_users import UsersDataBaseWorker
from user_scenariors.booking_service import BookingService

class BookingServiceFactory:
    """Фабрика для сервисов бронирования"""
    
    _services_cache = {}
    
    @classmethod
    def create_booking_service(cls, 
                              user_worker: UsersDataBaseWorker,
                              booking_worker: BookingsDataBaseWorker) -> BookingService:
        """Создает или возвращает кешированный экземпляр сервиса бронирования"""
        # Создаем составной ключ из ID обоих воркеров
        cache_key = f"{id(user_worker)}_{id(booking_worker)}"
        
        if cache_key not in cls._services_cache:
            cls._services_cache[cache_key] = BookingService(user_worker, booking_worker)
        
        return cls._services_cache[cache_key]