# handlers/datetime.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from states import MakeAppointment
from yclients import YClients
from dialogs_data import BotDialogData
from keyboards.time import get_day_keyboard, get_time_keyboard, confirm_day_and_time_keyboard
from utils.yclients_helpers import find_time_string_by_datetime
from handlers.appointment import return_to_main_menu_appointment

# Регистрация диалога выбора даты и времени
def register(dp):
	@dp.callback_query_handler(lambda call: "StartSelectDateAndTime" in call.data, state="*")
	async def start_select_time(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		if not yc.staff_id:
			await call.answer("Пожалуйста, сначала выберите специалиста.", show_alert=True)
			return
		if not yc.service_ids:
			await call.answer("Пожалуйста, сначала выберите услугу.", show_alert=True)
			return
		await state.set_state(MakeAppointment.select_day_and_time)
		await call.message.edit_text("📅 Выберите дату:", reply_markup=get_day_keyboard(yc))

	@dp.callback_query_handler(lambda call: "SelectedDay:" in call.data, state=MakeAppointment.select_day_and_time)
	async def select_day(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		datetime_value = call.data.replace("SelectedDay:", "")
		yc.set_datetime(datetime_value)
		dialog_data.day_name = yc.get_dates()[datetime_value]
		await state.set_state(MakeAppointment.get_time)
		await state.set_data(state_data)
		await call.message.edit_text("⌚ Выберите время:", reply_markup=get_time_keyboard(yc))

	@dp.callback_query_handler(lambda call: "SelectedTime:" in call.data, state=MakeAppointment.get_time)
	async def select_time(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		time = call.data.replace("SelectedTime:", "")
		yc.set_time(time)
		dialog_data.time = find_time_string_by_datetime(yc, time)
		await state.set_data(state_data)
		await call.message.edit_text(
			f"Вы действительно хотите выбрать дату и время: {dialog_data.day_name} в {dialog_data.time}?",
			reply_markup=confirm_day_and_time_keyboard(time)
		)

	@dp.callback_query_handler(lambda call: "ConfirmDayAndTime:" in call.data, state=MakeAppointment.get_time)
	async def confirm_time(call: CallbackQuery, state: FSMContext):
		await return_to_main_menu_appointment(call, state)

	@dp.callback_query_handler(lambda call: call.data == "ReturnToSelectDay", state=MakeAppointment.get_time)
	async def return_to_day(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		yc.set_datetime(None)
		await state.set_state(MakeAppointment.select_day_and_time)
		await call.message.edit_text("📅 Выберите дату:", reply_markup=get_day_keyboard(yc))

	@dp.callback_query_handler(lambda call: call.data == "TIMEReturnToMainMenu", state="*")
	async def cancel_time(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		dialog_data.day_name = ""
		dialog_data.time = ""
		yc.set_datetime(None)
		yc.set_time(None)
		await state.set_state(MakeAppointment.start_bot)
		await state.set_data(state_data)
		await return_to_main_menu_appointment(call, state)
