# handlers/confirm.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile
from states import MakeAppointment
from yclients import YClients
from dialogs_data import BotDialogData
from texts.templates import prepare_main_menu_template
from utils.calendar import generate_calendar_url, generate_ics_file
from storage.user_memory import remember_user, get_user_data, get_user_profile, remember_user_profile
from handlers.user_profile import ProfileForm
import logging
from datetime import datetime, timedelta
from handlers.appointment import return_to_main_menu_appointment

# Регистрация подтверждения записи и повторной попытки
def register(dp):
	@dp.callback_query_handler(lambda call: call.data == "StartFinalDialog", state="*")
	async def start_final_dialog(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		user_data = get_user_profile(call.from_user.id)  # заменено на полный профиль
		dialog_data: BotDialogData = state_data.get("data")
		if user_data.get("phone") and user_data.get("first_name"):
			full_name = f"{user_data.get('last_name', '')} {user_data.get('first_name', '')} {user_data.get('middle_name', '')}".strip()
			dialog_data.full_name = full_name
			dialog_data.phone_number = user_data.get("phone")
			state_data['data'] = dialog_data
			await state.set_data(state_data)
			keyboard = types.InlineKeyboardMarkup(row_width=2)
			keyboard.add(
				types.InlineKeyboardButton("✅ Использовать сохранённые данные", callback_data="UseStoredUserData"),
				types.InlineKeyboardButton("✏️ Ввести заново", callback_data="EnterUserData")
			)
			await call.message.edit_text(f"👤 Имя: {full_name}\n📞 Телефон: {user_data['phone']}\n\nВы хотите использовать эти данные?", reply_markup=keyboard)
		else:
			await call.message.edit_text("📞 Отправьте свой номер телефона начиная с +7")
			await state.set_state(MakeAppointment.get_phone_number)
			state_data['temp'] = call.message.message_id
			await state.set_data(state_data)

	@dp.callback_query_handler(lambda call: call.data == "UseStoredUserData", state="*")
	async def use_stored_user_data(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		dialog_data: BotDialogData = state_data.get("data")
		user_data = get_user_profile(call.from_user.id)
		dialog_data.phone_number = user_data.get("phone")
		dialog_data.full_name = f"{user_data.get('last_name', '')} {user_data.get('first_name', '')} {user_data.get('middle_name', '')}".strip()
		state_data['data'] = dialog_data
		await state.set_data(state_data)
		await state.set_state(MakeAppointment.get_comment)
		msg = await call.message.edit_text("Если хотите — добавьте комментарий, или нажмите 'Пропустить'", reply_markup=types.InlineKeyboardMarkup().add(
			types.InlineKeyboardButton(text="Пропустить", callback_data="SkipComment")
		))
		state_data['temp'] = msg.message_id
		await state.set_data(state_data)

	@dp.callback_query_handler(lambda call: call.data == "EnterUserData", state="*")
	async def enter_user_data(call: CallbackQuery, state: FSMContext):
		await call.message.edit_text("📞 Отправьте свой номер телефона начиная с +7")
		await state.set_state(MakeAppointment.get_phone_number)
		state_data = await state.get_data()
		state_data['temp'] = call.message.message_id
		await state.set_data(state_data)

	@dp.message_handler(state=MakeAppointment.get_phone_number)
	async def get_phone_number(message: types.Message, state: FSMContext):
		if not message.text.startswith(('+7', '8', '7')) or not message.text.replace('+', '').isdigit():
			await message.answer("Неверный номер. Пример: +79114689686")
			return
		state_data = await state.get_data()
		dialog_data: BotDialogData = state_data["data"]
		dialog_data.phone_number = message.text
		await state.set_state(MakeAppointment.get_fullname)
		await state.set_data(state_data)
		await message.bot.delete_message(message.chat.id, state_data['temp'])
		msg = await message.answer("👤 Отправьте своё имя")
		state_data['temp'] = msg.message_id
		await state.set_data(state_data)

	@dp.message_handler(state=MakeAppointment.get_fullname)
	async def get_fullname(message: types.Message, state: FSMContext):
		state_data = await state.get_data()
		dialog_data: BotDialogData = state_data["data"]
		dialog_data.full_name = message.text

		# Разбивка ФИО
		name_parts = message.text.strip().split()
		first_name = name_parts[0] if len(name_parts) > 0 else ""
		last_name = name_parts[1] if len(name_parts) > 1 else ""
		middle_name = name_parts[2] if len(name_parts) > 2 else ""

		# Сохраняем в БД
		remember_user_profile(
			user_id=message.from_user.id,
			first_name=first_name,
			last_name=last_name,
			middle_name=middle_name,
			phone=dialog_data.phone_number
		)

		await message.bot.delete_message(message.chat.id, state_data['temp'])
		msg = await message.answer("Если хотите — добавьте комментарий, или нажмите 'Пропустить'", reply_markup=types.InlineKeyboardMarkup().add(
			types.InlineKeyboardButton(text="Пропустить", callback_data="SkipComment")
		))
		state_data['temp'] = msg.message_id
		await state.set_state(MakeAppointment.get_comment)
		await state.set_data(state_data)

	@dp.message_handler(state=MakeAppointment.get_comment)
	async def get_comment(message: types.Message, state: FSMContext):
		state_data = await state.get_data()
		dialog_data: BotDialogData = state_data["data"]
		dialog_data.comment = message.text
		await message.bot.delete_message(message.chat.id, state_data['temp'])
		text = prepare_main_menu_template(dialog_data.staff_name, dialog_data.day_name, dialog_data.time, dialog_data.service_names, dialog_data.service_prices)
		text += f"\n👤 Имя: {dialog_data.full_name}\n📞 Телефон: {dialog_data.phone_number}"
		if dialog_data.comment:
			text += f"\n💬 Комментарий: {dialog_data.comment}"
		keyboard = types.InlineKeyboardMarkup(row_width=2)
		keyboard.add(
			types.InlineKeyboardButton("Да ✅", callback_data="ConfirmRecord"),
			types.InlineKeyboardButton("Нет ❌", callback_data="CancelRecord")
		)
		await message.answer(text, reply_markup=keyboard)

	@dp.callback_query_handler(lambda call: call.data == "SkipComment", state="*")
	async def skip_comment(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		dialog_data: BotDialogData = state_data["data"]
		text = prepare_main_menu_template(dialog_data.staff_name, dialog_data.day_name, dialog_data.time, dialog_data.service_names, dialog_data.service_prices)
		text += f"\n👤 Имя: {dialog_data.full_name}\n📞 Телефон: {dialog_data.phone_number}"
		keyboard = types.InlineKeyboardMarkup(row_width=2)
		keyboard.add(
			types.InlineKeyboardButton("Да ✅", callback_data="ConfirmRecord"),
			types.InlineKeyboardButton("Нет ❌", callback_data="CancelRecord")
		)
		await call.message.edit_text(text, reply_markup=keyboard)

	@dp.callback_query_handler(lambda call: call.data == "ConfirmRecord", state="*")
	async def confirm_record(call: CallbackQuery, state: FSMContext):
		state_data = await state.get_data()
		if "yc" not in state_data or "data" not in state_data:
			await call.message.edit_text("⚠️ Не удалось найти данные. Пожалуйста, начните заново.")
			await state.reset_state()
			return
		
		yc: YClients = state_data["yc"]
		dialog_data: BotDialogData = state_data["data"]

		# Получение email из профиля
		user_profile = get_user_profile(call.from_user.id)
		email = user_profile.get("email", "")

		resp = yc.send_record(
			dialog_data.full_name, 
			dialog_data.phone_number, 
			comment=dialog_data.comment,
			email=email if email else ""
		)
		logging.getLogger("yclients").info("YClients response: %s", resp)
		
		# Обработка ошибок
		if isinstance(resp, dict) and resp.get("errors"):
			error_data = resp.get("errors", {})
			meta_message = resp.get("meta", {}).get("message", "Произошла ошибка.")

			# Проверка на необходимость подтверждения (антибот)
			if "X-App-Validation-Token" in error_data and "X-App-Security-Level" in error_data:
				confirm_url = error_data["X-App-Security-Level"]["user_confirm"]["url"]
				await state.update_data(confirm_retry=True)
				keyboard = types.InlineKeyboardMarkup()
				keyboard.add(types.InlineKeyboardButton(text="✅ Перейти для подтверждения", url=confirm_url))
				keyboard.add(types.InlineKeyboardButton(text="🔁 Повторить запись", callback_data="RetryRecord"))
				await call.message.edit_text(
					"⚠️ *Не удалось записаться.*\n\nДля подтверждения, что вы не бот, пройдите по ссылке ниже и нажмите «Разрешить». "
					"Затем вернитесь и нажмите «Повторить запись».", reply_markup=keyboard
				)
				return
			else:
				await call.message.edit_text(f"⚠️ *Ошибка при записи:* {meta_message}")
				return
			
		if isinstance(resp, dict) and resp.get("errors"):
			meta_message = resp.get("meta", {}).get("message", "Произошла ошибка.")
			await call.message.edit_text(f"⚠️ *Ошибка при записи:* {meta_message}")
			return

		if isinstance(resp, list) and len(resp) > 0:
			record = resp[0].get("record", {})
			staff = record.get("staff", {})
			services = "\n".join([s.get("title", "") for s in record.get("services", [])])
			cost = sum([s.get("cost", 0) for s in record.get("services", [])])
			address = record.get("company", {}).get("address", "")

			dt_start = record.get("datetime", "")
			dt_start_obj = datetime.strptime(dt_start, "%Y-%m-%dT%H:%M:%S%z")
			dt_end_obj = dt_start_obj + timedelta(seconds=record.get("length", 0))

			calendar_url = generate_calendar_url(
				service_title=record["services"][0]["title"],
				company=record["company"],
				address=record["company"]["address"],
				staff_name=record["staff"]["name"],
				phones=record["company"]["phones"],
				dt_start_obj=dt_start_obj,
				dt_end_obj=dt_end_obj
			)

			ics_file = generate_ics_file(
				service_title=record["services"][0]["title"],
				company=record["company"],
				address=record["company"]["address"],
				staff_name=record["staff"]["name"],
				phones=record["company"]["phones"],
				dt_start_obj=dt_start_obj,
				dt_end_obj=dt_end_obj
			)

			text = f"✅ Запись создана!\n📅 {record.get('date', '')}\n👤 {staff.get('name', '')}\n🔧 {services}\n💵 {cost} ₽\n📍 {address}"
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton("🗓 В Google Календарь", url=calendar_url))
			await call.message.edit_text(text, reply_markup=keyboard)
			await call.bot.send_document(call.message.chat.id, ics_file, caption="📥 Файл для календаря")
		else:
			await call.message.edit_text("Запись подтверждена, но данные не получены.")

	@dp.callback_query_handler(lambda call: call.data == "RetryRecord", state="*")
	async def retry_record(call: CallbackQuery, state: FSMContext):
		await confirm_record(call, state)

	@dp.callback_query_handler(lambda call: call.data == "CancelRecord", state="*")
	async def cancel_record(call: CallbackQuery, state: FSMContext):
		await state.reset_state()
		await call.message.edit_text("⚠️ Запись отменена. Чтобы начать заново, нажмите 'Записаться на приём'")

	@dp.message_handler(commands=["profile"], state="*")
	async def open_profile(message: types.Message, state: FSMContext):
		from handlers.user_profile import start_profile_settings
		await start_profile_settings(message, state)

	@dp.callback_query_handler(lambda call: call.data == "EditProfile", state="*")
	async def callback_edit_profile(call: CallbackQuery, state: FSMContext):
		from handlers.user_profile import edit_profile_handler
		await edit_profile_handler(call, state)

	@dp.message_handler(state=ProfileForm.first_name)
	async def profile_first_name(message: types.Message, state: FSMContext):
		from handlers.user_profile import set_first_name
		await set_first_name(message, state)

	@dp.message_handler(state=ProfileForm.last_name)
	async def profile_last_name(message: types.Message, state: FSMContext):
		from handlers.user_profile import set_last_name
		await set_last_name(message, state)

	@dp.message_handler(state=ProfileForm.middle_name)
	async def profile_middle_name(message: types.Message, state: FSMContext):
		from handlers.user_profile import set_middle_name
		await set_middle_name(message, state)

	@dp.message_handler(state=ProfileForm.phone)
	async def profile_phone(message: types.Message, state: FSMContext):
		from handlers.user_profile import set_phone
		await set_phone(message, state)

	@dp.message_handler(state=ProfileForm.email)
	async def profile_email(message: types.Message, state: FSMContext):
		from handlers.user_profile import set_email
		await set_email(message, state)