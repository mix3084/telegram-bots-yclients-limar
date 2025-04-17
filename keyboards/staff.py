# keyboards/staff.py
from aiogram import types
from yclients import YClients
import logging

# Клавиатура выбора специалиста
def get_staff_keyboard(yc: YClients):
	buttons = []
	staff_list = yc.get_staff()

	if not isinstance(staff_list, list):
		logging.warning("yc.get_staff() вернул не список: %s", staff_list)
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		keyboard.add(types.InlineKeyboardButton(text="⚠️ Не удалось загрузить специалистов, сбросьте дату!", callback_data="ReturnToMainMenu"))
		return keyboard

	for staff in staff_list:
		if staff.get('bookable'):
			buttons.append(
				types.InlineKeyboardButton(
					text=staff['name'], callback_data=f"SelectedStaff:{staff['id']}"
				)
			)

	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(*buttons)
	keyboard.add(types.InlineKeyboardButton(text="Назад ❌", callback_data="ReturnToMainMenu"))
	return keyboard

# Клавиатура подтверждения специалиста
def confirm_staff_keyboard(staff_id, staff_name):
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.insert(types.InlineKeyboardButton(text="Подтвердить ✅", callback_data=f"ConfirmStaff:{staff_id}:{staff_name}"))
	keyboard.insert(types.InlineKeyboardButton(text="Отмена ❌", callback_data="ReturnToMainMenu"))
	return keyboard