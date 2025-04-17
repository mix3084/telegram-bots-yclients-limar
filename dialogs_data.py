# dialogs_data.py

# Класс хранения данных диалога между пользователем и ботом
class BotDialogData:
	def __init__(self):
		self.raw_data = {}
		self.user_id = None
		self.staff_name = None
		self.temp_service_ids = []
		self.service_names = []
		self.service_prices = []
		self.category_id = None
		self.day_name = None
		self.time = None
		self.full_name = None
		self.phone_number = None
		self.comment = ''