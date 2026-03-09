from aiogram.fsm.state import StatesGroup, State

class BookingStates(StatesGroup):
    choosing_range = State()
    choosing_amount = State()  # состояние ввода суммы оплаты/вознаграждения