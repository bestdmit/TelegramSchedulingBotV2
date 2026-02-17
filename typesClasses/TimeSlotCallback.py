from aiogram.filters.callback_data import CallbackData

class TimeSlotCallback(CallbackData,prefix="timeslot"):
    time:str
    action: str