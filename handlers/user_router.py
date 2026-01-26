from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.registerSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from database_workers.database_worker_for_users import UsersDataBaseWorker
from keyboards import get_main_menu, get_no_roles_menu
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message,state:FSMContext,userWorker:UsersDataBaseWorker):

    if (await userWorker.check_user(message.from_user.id)):
        menu = get_main_menu()
        await message.answer(f"Привет, {(await userWorker.get_user(message.from_user.id))["user_name"]}",
                             reply_markup = menu)
    else:
         menu = get_no_roles_menu()
         await message.answer("Введите своё имя:",
                            reply_markup = menu  )
         await state.set_state(RegisterSteps.wait_user_name)
         
         

@router.message(RegisterSteps.wait_user_name)
async def process_name(message:Message,state:FSMContext,userWorker:UsersDataBaseWorker):
    await userWorker.add_user(message.from_user.id,message.text)
    if await userWorker.check_user(message.from_user.id):
        menu = get_main_menu()
        await message.answer(f"Вы успешно добавлены,{message.text}",
                             reply_markup = menu)#потом нужно перенсти меню без ролей туда, где не будет ролей, а не отсутсвие полбзователя в таблице
        await state.clear()
        
        