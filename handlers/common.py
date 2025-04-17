# handlers/common.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from keyboards.misc import help_keyboard, map_keyboard
from handlers.user_profile import start_profile_settings
from config import MAIN_MENU_COMMANDS

# Регистрация хендлеров команд /start, /help и общей помощи
def register(dp):
	main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	main_menu_keyboard.add(*MAIN_MENU_COMMANDS)

	@dp.message_handler(commands=['start'], state='*')
	async def cmd_start(message: Message):
		await message.answer("Котик, привет!✨", reply_markup=main_menu_keyboard)

	@dp.message_handler(commands=['help'], state='*')
	@dp.message_handler(Text(equals="Помощь"), state='*')
	async def cmd_help(message: Message):
		txt = """
Здесь ты можешь посмотреть, как добратсья до нашей студии 🤍
Наш адрес: улица Марины Расковой, 4А ✨"""
		await message.answer(txt, reply_markup=help_keyboard())

	@dp.message_handler(Text(equals="Мои данные"), state='*')
	@dp.message_handler(commands=['profile'], state='*')
	async def cmd_profile(message: Message, state: FSMContext):
		await start_profile_settings(message, state)

	@dp.callback_query_handler(lambda call: call.data.endswith("_way"), state='*')
	async def show_map(call: CallbackQuery, state: FSMContext):
		captions = {
			"Station_way": "Как пройти от вокзала до студии",
			"Bus_way": "Как пройти с улицы Тургенева до студии",
		}
		file_name = call.data + ".jpg"
		await call.message.delete()
		await call.message.answer_photo(open(file_name, "rb"), caption=captions[call.data], reply_markup=map_keyboard(call.data))

	@dp.callback_query_handler(lambda call: call.data == "help_back", state='*')
	async def help_back(call: CallbackQuery, state: FSMContext):
		await cmd_help(call.message)
		await call.message.delete()
