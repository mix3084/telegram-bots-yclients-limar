# states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

# Состояния диалога записи на приём
class MakeAppointment(StatesGroup):
	start_bot = State()
	get_id = State()
	get_name = State()
	get_service = State()
	get_category = State()
	get_day = State()
	get_time = State()
	get_phone_number = State()
	get_fullname = State()
	get_comment = State()
	select_staff = State()
	select_services = State()
	select_services_category = State()
	select_day_and_time = State()