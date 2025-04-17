# main.py
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import logging
import config
from handlers import common, appointment, staff, services, datetime, confirm, user_profile, cancel
from utils.logging_config import setup_logging

# Настройка логирования
setup_logging()

bot = Bot(token=config.token, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())

# Регистрация хендлеров
common.register(dp)
appointment.register(dp)
staff.register(dp)
services.register(dp)
datetime.register(dp)
confirm.register(dp)
cancel.register(dp)

if __name__ == '__main__':
	executor.start_polling(dp)
