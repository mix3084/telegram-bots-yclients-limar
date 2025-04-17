# keyboards/services.py
from aiogram import types
from yclients import YClients
from dialogs_data import BotDialogData
from utils.yclients_helpers import find_category_by_id
import logging

# Клавиатура выбора категорий услуг
def get_categories_keyboard(yc: YClients, dialog_data: BotDialogData):
	small_buttons = []
	big_buttons = []
	keyboard = types.InlineKeyboardMarkup(row_width=2)

	categories = yc.get_categories_and_services()
	if not isinstance(categories, dict):
		logging.warning("yc.get_categories_and_services() вернул не словарь: %s", categories)
		keyboard.add(types.InlineKeyboardButton(text="⚠️ Не удалось загрузить категории", callback_data="ReturnToMainMenu"))
		return keyboard

	for category_id, data in categories.items():
		btn = types.InlineKeyboardButton(text=data['title'], callback_data=f"SelectedCategory:{category_id}")
		if len(data['title']) >= 18:
			big_buttons.append(btn)
		else:
			small_buttons.append(btn)
	keyboard.add(*small_buttons)
	for button in big_buttons:
		keyboard.row()
		keyboard.add(button)
	keyboard.row()

	if dialog_data.temp_service_ids:
		keyboard.add(types.InlineKeyboardButton(text="Закончить выбор ✅", callback_data="SERVICESFinishSelection"))
		keyboard.add(types.InlineKeyboardButton(text="Сбросить выбранные услуги ❌", callback_data="SERVICESResetSelections"))
	else:
		keyboard.add(types.InlineKeyboardButton(text="Вернуться в основное меню ⬅️", callback_data="ReturnToMainMenu"))
	return keyboard

# Клавиатура выбора услуг внутри категории
def get_services_keyboard(yc: YClients, dialog_data: BotDialogData, category_id):
	small_buttons = []
	big_buttons = []
	service_names = []
	keyboard = types.InlineKeyboardMarkup(row_width=2)

	category = find_category_by_id(yc, category_id)
	if not category or 'services' not in category:
		logging.warning("Категория не найдена или не содержит услуг: %s", category)
		keyboard.add(types.InlineKeyboardButton(text="⚠️ Услуги не найдены", callback_data="SERVICESReturnToCategories"))
		return keyboard, service_names
	
	for service in category['services']:
		button_text = f"{service['title']} | {service['price']}р"
		if int(service['id']) not in dialog_data.temp_service_ids:
			callback = f"SelectedService:{category_id}:{service['id']}"
		else:
			button_text = f"❌ Отменить выбор {service['title']}"
			callback = f"UnselectedService:{category_id}:{service['id']}"
		btn = types.InlineKeyboardButton(text=button_text, callback_data=callback)
		if len(service['title']) >= 18:
			big_buttons.append(btn)
		else:
			small_buttons.append(btn)
		service_names.append(btn.text)
	keyboard.add(*small_buttons)
	for button in big_buttons:
		keyboard.row()
		keyboard.add(button)
	keyboard.row()
	keyboard.add(types.InlineKeyboardButton(text="Вернуться к категориям ⬅️️", callback_data="SERVICESReturnToCategories"))
	keyboard.add(types.InlineKeyboardButton(text="Отмена ❌", callback_data="ReturnToMainMenu"))
	if dialog_data.temp_service_ids:
		keyboard.add(types.InlineKeyboardButton(text="Закончить выбор ✅", callback_data="SERVICESFinishSelection"))
	return keyboard, service_names