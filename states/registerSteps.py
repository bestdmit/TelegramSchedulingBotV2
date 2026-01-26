from aiogram.fsm.state import StatesGroup, State
class RegisterSteps(StatesGroup):
    wait_user_name = State()