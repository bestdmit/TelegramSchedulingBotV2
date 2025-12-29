from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import SUBJECTS

def generate_subjects_keyboard(selected_subjects=None):
    builder = InlineKeyboardBuilder()
    selected = selected_subjects or []
    
    for subject_id, subject_name in SUBJECTS.items():
        emoji = "✅" if subject_id in selected else "⬜️"
        builder.button(
            text=f"{emoji} {subject_name}",
            callback_data=f"subject_{subject_id}"
        )
    
    builder.button(text="✅ Готово", callback_data="subjects_done")
    builder.adjust(2)
    return builder.as_markup()