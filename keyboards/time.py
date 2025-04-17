# keyboards/time.py
from aiogram import types
from yclients import YClients

# Клавиатура выбора дня
def get_day_keyboard(yc: YClients):
	buttons = [
		types.InlineKeyboardButton(text=day, callback_data=f"SelectedDay:{datetime}")
		for datetime, day in yc.get_dates().items()
	]
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(*buttons)
	keyboard.add(types.InlineKeyboardButton(text="Вернуться в основное меню ⬅️", callback_data="TIMEReturnToMainMenu"))
	return keyboard

# Клавиатура выбора времени
def get_time_keyboard(yc: YClients):
	buttons = [
		types.InlineKeyboardButton(text=slot['time'], callback_data=f"SelectedTime:{slot['datetime']}")
		for slot in yc.get_times()
	]
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(*buttons)
	keyboard.add(types.InlineKeyboardButton(text="Вернуться к выбору дня ⬅️", callback_data="ReturnToSelectDay"))
	return keyboard

# Подтверждение выбранного времени
def confirm_day_and_time_keyboard(time_value):
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.insert(types.InlineKeyboardButton(
		text="Подтвердить ✅",
		callback_data=f"ConfirmDayAndTime:{time_value}"  # 👈 здесь теперь подставляется значение времени
	))
	keyboard.insert(types.InlineKeyboardButton(
		text="Отмена ❌",
		callback_data="TIMEReturnToMainMenu"
	))
	return keyboard
