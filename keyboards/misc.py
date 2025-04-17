# keyboards/misc.py
from aiogram import types

# Кнопка "Пропустить комментарий"
def skip_comment_keyboard():
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="SkipComment"))
	return keyboard

# Клавиатура помощи с маршрутами
def help_keyboard():
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(types.InlineKeyboardButton(text="Путь от вокзала", callback_data="Station_way"))
	keyboard.add(types.InlineKeyboardButton(text="Путь от улицы Тургенева", callback_data="Bus_way"))
	return keyboard

# Клавиатура с ссылкой на Яндекс карты
def map_keyboard(map_type):
	map_types = {
		"Station_way": "https://yandex.ru/maps/20139/zelenogradsk/?ll=20.480044%2C54.956203&mode=routes&rtext=54.958322%2C20.473216~54.956451%2C20.486302",
		"Bus_way": "https://yandex.ru/maps/20139/zelenogradsk/?ll=20.485793%2C54.954889&mode=routes&rtext=54.953318%2C20.483469~54.956451%2C20.486302",
	}
	keyboard = types.InlineKeyboardMarkup(row_width=1)
	keyboard.add(types.InlineKeyboardButton(text="Открыть в Яндекс Картах", url=map_types[map_type]))
	keyboard.add(types.InlineKeyboardButton(text="Вернуться назад", callback_data="help_back"))
	return keyboard