# handlers/staff.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from states import MakeAppointment
from yclients import YClients
from dialogs_data import BotDialogData
from keyboards.staff import get_staff_keyboard, confirm_staff_keyboard
from handlers.appointment import return_to_main_menu_appointment
from utils.yclients_helpers import find_staff_by_id

# Регистрация диалога выбора специалиста
def register(dp):
	@dp.callback_query_handler(lambda call: "StartSelectStaff" in call.data, state="*")
	async def start_select_staff(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		await state.set_state(MakeAppointment.select_staff)
		await call.message.edit_text("Выберите специалиста:", reply_markup=get_staff_keyboard(yc))

	@dp.callback_query_handler(lambda call: "SelectedStaff:" in call.data, state=MakeAppointment.select_staff)
	async def confirm_dialog_selected_staff(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		staff_id = call.data.replace("SelectedStaff:", "")
		staff = find_staff_by_id(yc, int(staff_id))
		await call.message.edit_text(
			f"Вы действительно хотите выбрать специалиста: {staff['name']}",
			reply_markup=confirm_staff_keyboard(staff_id, staff['name'])
		)

	@dp.callback_query_handler(lambda call: "ConfirmStaff:" in call.data, state=MakeAppointment.select_staff)
	async def confirm_selected_staff(call: CallbackQuery, state: FSMContext):
		staff_id, staff_name = call.data.replace("ConfirmStaff:", "").split(":")
		state_data = await state.get_data()
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]
		yc.set_staff_id(int(staff_id))
		dialog_data.staff_name = staff_name
		await state.set_data({"data": dialog_data, "yc": yc})
		await return_to_main_menu_appointment(call, state)
