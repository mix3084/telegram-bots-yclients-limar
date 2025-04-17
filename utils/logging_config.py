# utils/logging_config.py
import logging
import os

# Настройка логирования в консоль и файл

def setup_logging():
	os.makedirs("logs", exist_ok=True)
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
		handlers=[
			logging.FileHandler("logs/bot.log", encoding="utf-8"),
			logging.StreamHandler()
		]
	)
	logging.getLogger("aiogram").setLevel(logging.WARNING)