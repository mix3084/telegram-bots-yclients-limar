# handlers/cancel.py
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from states import MakeAppointment
from handlers.appointment import return_to_main_menu_appointment

# Обработка отмены и возврата в главное меню
def register(dp):
	@dp.callback_query_handler(lambda call: call.data == "ReturnToMainMenu", state="*")
	async def return_main_menu(call: CallbackQuery, state: FSMContext):
		await state.set_state(MakeAppointment.start_bot)
		await return_to_main_menu_appointment(call, state)

	@dp.callback_query_handler(lambda call: call.data == "TIMEReturnToMainMenu", state="*")
	async def reject_time(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc = state_data["yc"]
		dialog_data = state_data["data"]
		dialog_data.day_name = ""
		dialog_data.time = ""
		yc.set_datetime(None)
		yc.set_time(None)
		await state.set_state(MakeAppointment.start_bot)
		await state.set_data(state_data)
		await return_to_main_menu_appointment(call, state)

	@dp.callback_query_handler(lambda call: call.data == "CancelEntry", state="*")
	async def cancel_entry(call: CallbackQuery, state: FSMContext):
		await state.set_state(MakeAppointment.start_bot)
		await return_to_main_menu_appointment(call, state)
