# handlers/appointment.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from states import MakeAppointment
from dialogs_data import BotDialogData
from yclients import YClients
from keyboards.main_menu import get_main_menu_keyboard
from texts.templates import prepare_main_menu_template
from config import MAIN_MENU_COMMANDS
import logging

logger = logging.getLogger(__name__)

# Регистрация хендлеров запуска записи и возврата в меню
def register(dp):
	@dp.message_handler(lambda message: message.text == "Записаться на прием", state="*")
	async def make_appointment(message: Message, state: FSMContext):
		# Принудительное обновление меню-кнопок
		keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
		keyboard.add(*MAIN_MENU_COMMANDS)
		await message.answer("Меню обновлено ✨", reply_markup=keyboard)
		yc = YClients(shop_id=792768, company_id=743866)
		dialog_data = BotDialogData()
		await state.set_state(MakeAppointment.start_bot)
		await state.set_data({"data": dialog_data, "yc": yc})
		await message.answer(prepare_main_menu_template(), reply_markup=get_main_menu_keyboard(yc))

	@dp.callback_query_handler(lambda call: "CancelEntry" in call.data, state="*")
	async def cancel_entry(call: CallbackQuery, state: FSMContext):
		yc = YClients(shop_id=792768, company_id=743866)
		dialog_data = BotDialogData()
		await state.set_state(MakeAppointment.start_bot)
		await state.set_data({"data": dialog_data, "yc": yc})
		await call.message.edit_text(
			prepare_main_menu_template(dialog_data.staff_name, dialog_data.day_name, dialog_data.time, dialog_data.service_names, dialog_data.service_prices),
			reply_markup=get_main_menu_keyboard(yc)
		)

# Вспомогательные функции для возврата
async def return_to_main_menu_appointment(call: CallbackQuery, state: FSMContext):
	try:
		logger.info("Возврат в главное меню: получаем состояние пользователя")
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]

		logger.info("Формируем меню: staff=%s, day=%s, time=%s, services=%s",
			dialog_data.staff_name, dialog_data.day_name, dialog_data.time, dialog_data.service_names)

		text = prepare_main_menu_template(
			dialog_data.staff_name,
			dialog_data.day_name,
			dialog_data.time,
			dialog_data.service_names,
			dialog_data.service_prices
		)

		logger.info("Отправка меню пользователю")
		await call.message.edit_text(
			text,
			reply_markup=get_main_menu_keyboard(yc)
		)
	except Exception as e:
		logger.exception("Ошибка при возврате в главное меню: %s", str(e))
		await call.message.answer("⚠️ Произошла ошибка при возврате в меню. Попробуйте ещё раз.")

async def cancel_appointment(call: CallbackQuery, state: FSMContext):
	state_data = await state.get_data()
	yc: YClients = state_data["yc"]
	dialog_data: BotDialogData = state_data["data"]
	await call.message.edit_text(prepare_main_menu_template(), reply_markup=get_main_menu_keyboard(yc))
