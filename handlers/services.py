# handlers/services.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from states import MakeAppointment
from yclients import YClients
from dialogs_data import BotDialogData
from keyboards.services import get_categories_keyboard, get_services_keyboard
from utils.yclients_helpers import find_category_by_id, convert_service_ids_to_service_names, convert_service_ids_to_service_prices
from handlers.appointment import return_to_main_menu_appointment

# Регистрация диалога выбора услуг и категорий
def register(dp):
	@dp.callback_query_handler(lambda call: "StartSelectServices" in call.data, state="*")
	async def start_select_services(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		if not yc.staff_id:
			await call.answer("Пожалуйста, сначала выберите специалиста.", show_alert=True)
			return
		await state.set_state(MakeAppointment.select_services_category)
		await call.message.edit_text("Выберите категорию:", reply_markup=get_categories_keyboard(yc, state_data["data"]))

	@dp.callback_query_handler(lambda call: "SelectedCategory:" in call.data, state=MakeAppointment.select_services_category)
	async def set_selected_category(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		category_id = call.data.replace("SelectedCategory:", "")
		dialog_data.category_id = category_id
		state_data["data"] = dialog_data
		await state.set_state(MakeAppointment.get_service)
		await state.set_data(state_data)
		keyboard, service_names = get_services_keyboard(yc, dialog_data, category_id)
		await call.message.edit_text(
			f"🔧 Выберите услугу: {find_category_by_id(yc, category_id)['title']}\n" +
			"\n".join(service_names) +
			f"\n\nВсего услуг в этой категории: {len(service_names)}",
			reply_markup=keyboard
		)

	@dp.callback_query_handler(lambda call: "SelectedService:" in call.data, state=MakeAppointment.get_service)
	async def set_selected_service(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		service_id = call.data.split(":")[-1]
		dialog_data.temp_service_ids.append(int(service_id))
		dialog_data.day_name = ""
		dialog_data.time = ""
		yc.set_datetime("")
		yc.set_time("")
		await state.set_data(state_data)
		keyboard, _ = get_services_keyboard(yc, dialog_data, dialog_data.category_id)
		await call.message.edit_reply_markup(keyboard)

	@dp.callback_query_handler(lambda call: "UnselectedService:" in call.data, state=MakeAppointment.get_service)
	async def set_unselected_service(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		service_id = call.data.split(":")[-1]
		dialog_data.temp_service_ids.remove(int(service_id))
		dialog_data.day_name = ""
		dialog_data.time = ""
		yc.set_datetime("")
		yc.set_time("")
		await state.set_data(state_data)
		keyboard, _ = get_services_keyboard(yc, dialog_data, dialog_data.category_id)
		await call.message.edit_reply_markup(keyboard)

	@dp.callback_query_handler(lambda call: "SERVICESReturnToCategories" in call.data, state=MakeAppointment.get_service)
	async def return_to_categories(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		await state.set_state(MakeAppointment.select_services_category)
		await call.message.edit_text("Выберите категорию:", reply_markup=get_categories_keyboard(state_data["yc"], state_data["data"]))

	@dp.callback_query_handler(lambda call: "SERVICESFinishSelection" in call.data, state="*")
	async def finish_selection(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		yc.reset_service_ids()
		for service_id in dialog_data.temp_service_ids:
			yc.add_service_id(int(service_id))
		dialog_data.service_names = convert_service_ids_to_service_names(yc, dialog_data.temp_service_ids)
		dialog_data.service_prices = convert_service_ids_to_service_prices(yc, dialog_data.temp_service_ids)
		state_data["yc"] = yc
		state_data["data"] = dialog_data
		await state.set_data(state_data)
		await state.set_state(MakeAppointment.start_bot)
		await return_to_main_menu_appointment(call, state)

	@dp.callback_query_handler(lambda call: "SERVICESResetSelections" in call.data, state="*")
	async def reset_selections(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		dialog_data.service_names.clear()
		dialog_data.service_prices.clear()
		dialog_data.temp_service_ids.clear()
		dialog_data.day_name = ""
		dialog_data.time = ""
		yc.set_datetime("")
		yc.set_time("")
		yc.reset_service_ids()
		await state.set_data(state_data)
		await return_to_main_menu_appointment(call, state)