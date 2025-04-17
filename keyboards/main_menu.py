# keyboards/main_menu.py
from aiogram import types
from yclients import YClients

# Клавиатура главного меню записи на прием
def get_main_menu_keyboard(yc: YClients):
	keyboard = types.InlineKeyboardMarkup(row_width=1)
	keyboard.add(types.InlineKeyboardButton(text="👤 Выбрать специалиста", callback_data="StartSelectStaff"))
	keyboard.add(types.InlineKeyboardButton(text="🔧 Выбрать услуги", callback_data="StartSelectServices"))
	keyboard.add(types.InlineKeyboardButton(text="📅 Выбрать дату и время", callback_data="StartSelectDateAndTime"))
	if yc.staff_id and yc.service_ids and yc.time:
		keyboard.add(types.InlineKeyboardButton(text="✅ Подтвердить запись", callback_data="StartFinalDialog"))
	if yc.staff_id or yc.service_ids or yc.time:
		keyboard.add(types.InlineKeyboardButton(text="❌ Отменить запись", callback_data="CancelEntry"))
	return keyboard
