from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from storage.user_memory import remember_user_profile, get_user_profile

class ProfileForm(StatesGroup):
	first_name = State()
	last_name = State()
	middle_name = State()
	phone = State()
	email = State()

async def start_profile_settings(message: types.Message, state: FSMContext):
	profile = get_user_profile(message.from_user.id)
	if profile:
		text = f"\n*Ваши текущие данные:*\n"
		text += f"👤 ФИО: {profile.get('last_name', '-')} {profile.get('first_name', '-')} {profile.get('middle_name', '-')}\n"
		text += f"📞 Телефон: {profile.get('phone', '-')}, ✉️ Email: {profile.get('email', '-')}\n"
	else:
		text = "У вас пока нет сохранённых данных. Давайте заполним!"
	keyboard = types.InlineKeyboardMarkup()
	keyboard.add(types.InlineKeyboardButton("✏️ Изменить данные", callback_data="EditProfile"))
	await message.answer(text, reply_markup=keyboard)

async def edit_profile_handler(call: CallbackQuery, state: FSMContext):
	await call.message.edit_text("Введите ваше *имя*:", parse_mode='Markdown')
	await state.set_state(ProfileForm.first_name)

async def set_first_name(message: types.Message, state: FSMContext):
	await state.update_data(first_name=message.text)
	await message.answer("Введите вашу *фамилию* (если есть, или напишите -):", parse_mode='Markdown')
	await state.set_state(ProfileForm.last_name)

async def set_last_name(message: types.Message, state: FSMContext):
	await state.update_data(last_name=message.text)
	await message.answer("Введите ваше *отчество* (если есть, или напишите -):", parse_mode='Markdown')
	await state.set_state(ProfileForm.middle_name)

async def set_middle_name(message: types.Message, state: FSMContext):
	await state.update_data(middle_name=message.text)
	await message.answer("Введите ваш *телефон* начиная с +7:", parse_mode='Markdown')
	await state.set_state(ProfileForm.phone)

async def set_phone(message: types.Message, state: FSMContext):
	if not message.text.startswith('+7') or not message.text[1:].isdigit():
		await message.answer("Неверный формат телефона. Пример: +79001234567")
		return
	await state.update_data(phone=message.text)
	await message.answer("Введите ваш *email* (если есть, или напишите -):", parse_mode='Markdown')
	await state.set_state(ProfileForm.email)

async def set_email(message: types.Message, state: FSMContext):
	await state.update_data(email=message.text)
	user_data = await state.get_data()
	remember_user_profile(
		user_id=message.from_user.id,
		first_name=user_data.get("first_name"),
		last_name=user_data.get("last_name"),
		middle_name=user_data.get("middle_name"),
		phone=user_data.get("phone"),
		email=user_data.get("email")
	)
	await message.answer("✅ Данные успешно сохранены!")
	await state.finish()
