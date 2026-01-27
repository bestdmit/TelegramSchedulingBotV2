from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.registerSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from database_workers.database_worker_for_users import UsersDataBaseWorker
user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message,state:FSMContext,userWorker:UsersDataBaseWorker):
    if (await userWorker.check_user(message.from_user.id)):
        await message.answer(f"Привет, {(await userWorker.get_user(message.from_user.id))["user_name"]}")
    else:
         await message.answer("Введите своё имя:")
         await state.set_state(RegisterSteps.wait_user_name)

@user_router.message(Command("delete"))
async def delete_myself(message: Message,userWorker:UsersDataBaseWorker):
    if (await userWorker.check_user(message.from_user.id)):
        await userWorker.delete_user(message.from_user.id)
    else:
        await message.answer("Вы не были зарегистрированы")
    

@user_router.message(RegisterSteps.wait_user_name)
async def process_name(message:Message,state:FSMContext,userWorker:UsersDataBaseWorker):
    await userWorker.add_user(message.from_user.id,message.text)
    if await userWorker.check_user(message.from_user.id):
        await message.answer(f"Вы успешно добавлены,{message.text}")
    else:
        await message.answer(f"Ошибка добавления")