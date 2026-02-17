from database_workers.database_worker_for_bookings import BookingsDataBaseWorker
from database_workers.database_worker_for_users import UsersDataBaseWorker
from user_scenariors.booking_service import BookingService
from user_scenariors.bookings_list import BookingsListService
class BookingServiceFactory:
    """Фабрика для сервисов бронирования"""
    
    _services_cache = {}
    
    @classmethod
    def _get_from_cache(cls, service_class, *workers):
        # Создаем ключ на основе типа класса и ID всех переданных воркеров
        workers_ids = "_".join([str(id(w)) for w in workers])
        cache_key = f"{service_class.__name__}_{workers_ids}"
        
        if cache_key not in cls._services_cache:
            cls._services_cache[cache_key] = service_class(*workers)
        
        return cls._services_cache[cache_key]

    @classmethod
    def create_booking_service(cls, 
                              user_worker: UsersDataBaseWorker,
                              booking_worker: BookingsDataBaseWorker) -> BookingService:
        """Создает или возвращает сервис создания бронирований"""
        return cls._get_from_cache(BookingService, user_worker, booking_worker)

    @classmethod
    def create_bookings_list_service(cls, 
                                    user_worker: UsersDataBaseWorker,
                                    booking_worker: BookingsDataBaseWorker) -> BookingsListService:
        """Создает или возвращает сервис просмотра списка бронирований"""
        return cls._get_from_cache(BookingsListService, user_worker, booking_worker)
