from aiogram.fsm.state import StatesGroup, State
class BookingStates(StatesGroup):
    choosing_range = State()