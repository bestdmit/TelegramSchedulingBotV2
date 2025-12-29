import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import BOT_TOKEN, ADMIN_IDS, is_admin
from database import db
from states import RegistrationStates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    user = await db.get_user(user_id)
    if user:
        user_name = user.get('user_name', '')
        roles = await db.get_user_roles(user_id)
        
        if roles:
            if is_admin(user_id):
                keyboard = types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton(text="➕ Добавить роль пользователю")]],
                    resize_keyboard=True
                )
                await message.answer(f"С возвращением, {user_name}!", reply_markup=keyboard)
            else:
                await message.answer(f"С возвращением, {user_name}!")
        else:
            await message.answer(f"✅ ФИО сохранено: {user_name}\n⏳ Обратитесь к администратору.", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Добро пожаловать!\nВведите ваше полное ФИО (имя и фамилия):", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.INPUT_NAME)

@dp.message(RegistrationStates.INPUT_NAME)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.text.strip()

    if len(user_name.split()) < 2:
        await message.answer("Пожалуйста, введите имя и фамилию:")
        return

    await db.save_user(user_id, user_name, "", "")
    
    await message.answer(f"✅ ФИО сохранено: {user_name}\n⏳ Обратитесь к администратору.")
    
    for admin_id in ADMIN_IDS:
        try:
            admin_kb = InlineKeyboardBuilder()
            admin_kb.button(text="👨‍🏫 Преподаватель", callback_data=f"admin_add_teacher_{user_id}")
            admin_kb.button(text="👨‍🎓 Ученик", callback_data=f"admin_add_student_{user_id}")
            admin_kb.button(text="👨‍👩‍👧‍👦 Родитель", callback_data=f"admin_add_parent_{user_id}")
            admin_kb.adjust(1)
            
            await bot.send_message(
                admin_id,
                f"🆕 Новый пользователь:\nID: {user_id}\nИмя: {user_name}",
                reply_markup=admin_kb.as_markup()
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить админа {admin_id}: {e}")
    
    await state.clear()

@dp.callback_query(F.data.startswith("admin_add_parent_"))
async def admin_add_parent(callback: types.CallbackQuery):
    user_id = int(callback.data.replace("admin_add_parent_", ""))
    
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    user_name = user.get('user_name', '')
    current_roles = await db.get_user_roles(user_id)
    
    new_roles = set(current_roles)
    new_roles.add("parent")
    
    await db.save_user(user_id, user_name, ','.join(new_roles), "")
    
    await callback.message.edit_text(f"✅ Роль родителя добавлена пользователю {user_name}")
    
    try:
        await bot.send_message(user_id, "✅ Вам добавлена роль *Родитель*!", parse_mode="Markdown")
    except:
        pass
    
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_add_teacher_"))
async def admin_add_teacher_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.replace("admin_add_teacher_", ""))
    
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    user_name = user.get('user_name', '')
    
    from keyboards import generate_subjects_keyboard
    
    await state.update_data(
        target_user_id=user_id,
        target_user_name=user_name,
        target_role="teacher"
    )
    
    await callback.message.edit_text(
        f"Добавление преподавателя: {user_name}",
        reply_markup=generate_subjects_keyboard([])
    )
    await state.set_state(RegistrationStates.SELECT_SUBJECTS)
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_add_student_"))
async def admin_add_student_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.replace("admin_add_student_", ""))
    
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    user_name = user.get('user_name', '')
    
    from keyboards import generate_subjects_keyboard
    
    await state.update_data(
        target_user_id=user_id,
        target_user_name=user_name,
        target_role="student"
    )
    
    await callback.message.edit_text(
        f"Добавление ученика: {user_name}",
        reply_markup=generate_subjects_keyboard([])
    )
    await state.set_state(RegistrationStates.SELECT_SUBJECTS)
    await callback.answer()

@dp.callback_query(RegistrationStates.SELECT_SUBJECTS, F.data.startswith("subject_"))
async def admin_select_subject(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_subjects", [])
    subj_id = callback.data.replace("subject_", "")
    
    if subj_id in selected:
        selected.remove(subj_id)
    else:
        selected.append(subj_id)
    
    await state.update_data(selected_subjects=selected)
    
    from keyboards import generate_subjects_keyboard
    await callback.message.edit_reply_markup(reply_markup=generate_subjects_keyboard(selected))
    await callback.answer()

@dp.callback_query(RegistrationStates.SELECT_SUBJECTS, F.data == "subjects_done")
async def admin_finish_subjects(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_subjects", [])
    role = data.get("target_role")
    user_id = data.get("target_user_id")
    user_name = data.get("target_user_name", "")
    
    if not selected:
        await callback.answer("Выберите хотя бы один предмет", show_alert=True)
        return
    
    success = await db.add_role_with_subjects(user_id, role, selected)
    
    if success:
        from config import SUBJECTS
        subject_names = [SUBJECTS.get(sid, sid) for sid in selected]
        
        await callback.message.edit_text(f"✅ Роль {role} добавлена!\nПредметы: {', '.join(subject_names)}")
        
        role_text = "Преподаватель" if role == "teacher" else "Ученик"
        
        try:
            await bot.send_message(
                user_id,
                f"✅ Вам добавлена роль *{role_text}*!\n📚 Предметы: {', '.join(subject_names)}",
                parse_mode="Markdown"
            )
        except:
            pass
    else:
        await callback.message.edit_text("❌ Ошибка при добавлении роли")
    
    await state.clear()
    await callback.answer()

async def main():
    await db.connect()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())