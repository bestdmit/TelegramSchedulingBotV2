from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from states.registerSteps import RegisterSteps
from aiogram.fsm.context import FSMContext
from database_workers.database_worker_for_users import UsersDataBaseWorker
from database_workers.database_worker_for_parents import ParentsDataBaseWorker
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from config import admin_ids
from keyboards import get_main_menu, get_no_roles_menu
user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message,state:FSMContext,userWorker:UsersDataBaseWorker):

    if (await userWorker.check_user(message.from_user.id)):
        user = await userWorker.get_user(message.from_user.id)
        roles = user.get("roles", "") if user else ""
        is_parent = "parent" in roles if roles else False
        menu = get_main_menu(parent=is_parent)
        await message.answer(f"Привет, {user.get('user_name')}", reply_markup=menu)
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
    

@user_router.message(F.text == "Обратиться к администратору")
async def handle_contact_admin(message: Message):
    await message.answer(
        "Для получения помощи обратитесь к администратору\n"
        "Телефон администратора: +79001372727\n\n"
    )

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


# Просмотр привязанных детей
@user_router.message(F.text == "Мои дети")
async def show_my_children(message: Message,
                           userWorker: UsersDataBaseWorker,
                           parentsWorker: ParentsDataBaseWorker):
    if not await userWorker.check_user(message.from_user.id):
        await message.answer("Вы не зарегистрированы")
        return

    childrens = await parentsWorker.get_children(message.from_user.id)
    if not childrens:
        await message.answer("У вас нет привязанных детей.")
        return

    builder = InlineKeyboardBuilder()
    text = "Ваши дети:\n"
    for cid in childrens:
        user = await userWorker.get_user(cid)
        name = user.get('user_name') if user else str(cid)
        text += f"{name}\n"
        builder.button(text=f"Записать {name}", callback_data=f"booking_child_{cid}")

    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup())


        
        
