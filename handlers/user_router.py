from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.registerSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from database_workers.database_worker_for_users import UsersDataBaseWorker
from config import admin_ids
from keyboards import get_main_menu, get_no_roles_menu
user_router = Router()

@user_router.message(Command("start"))
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
         
         

@user_router.message(Command("delete"))
async def delete_myself(message: Message,userWorker:UsersDataBaseWorker):
    if (await userWorker.check_user(message.from_user.id)):
        await userWorker.delete_user(message.from_user.id)
    else:
        await message.answer("Вы не были зарегистрированы")
    

@user_router.message(RegisterSteps.wait_user_name)
async def process_name(message:Message,state:FSMContext,userWorker:UsersDataBaseWorker,bot:Bot):
    await userWorker.add_user(message.from_user.id,message.text)
    if await userWorker.check_user(message.from_user.id):
        await message.answer(f"Вы успешно добавлены,{message.text}")
        for admin_id in admin_ids:
            await bot.send_message(
                chat_id=admin_id,
                text=f"Новый зарегистрированный пользователь: {message.text}\n ID:{message.from_user.id}"
                )
        await state.clear()
    else:
        await message.answer(f"Ошибка добавления")
        await state.clear()
        # menu = get_main_menu()
        # await message.answer(f"Вы успешно добавлены,{message.text}",
        #                      reply_markup = menu)#потом нужно перенсти меню без ролей туда, где не будет ролей, а не отсутсвие полбзователя в таблице
        # await state.clear()
        
        
