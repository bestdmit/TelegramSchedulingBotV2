# from aiogram.fsm.state import State, StatesGroup

# class RegistrationStates(StatesGroup):
#     INPUT_NAME = State()

# class AdminStates(StatesGroup):
#     SEARCH_USER = State()
#     SELECT_ROLE = State()
#     SELECT_SUBJECTS = State()
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    INPUT_NAME = State()
    SELECT_SUBJECTS = State()