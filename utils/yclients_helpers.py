# utils/yclients_helpers.py
from yclients import YClients

# Поиск специалиста по ID
def find_staff_by_id(yc: YClients, staff_id: int):
	for staff in yc.get_staff():
		if staff['id'] == staff_id:
			return staff
	return "None"

# Поиск услуги по ID в рамках категории
def find_service_by_id(yc: YClients, category_id, service_id):
	for service in yc.get_categories_and_services().get(int(category_id), {}).get('services', []):
		if service['id'] == int(service_id):
			return service
	return "None"

# Поиск категории по ID
def find_category_by_id(yc, category_id):
	return yc.get_categories_and_services().get(int(category_id), None)

# Поиск услуги по ID в списке всех услуг
def find_raw_service_by_id(yc: YClients, service_id):
	for service in yc.get_raw_services():
		if service['id'] == int(service_id):
			return service
	return "None"

# Поиск строки времени по datetime
def find_time_string_by_datetime(yc, datetime):
	for time in yc.get_times():
		if time['datetime'] == datetime:
			return time['time']
	return "None"

# Преобразование ID услуг в список названий
def convert_service_ids_to_service_names(yc: YClients, service_ids):
	services = yc.get_raw_services()
	service_names = []
	for service in services:
		if int(service['id']) in service_ids:
			service_names.append(f"{service['title']} | {service['price_max']} ₽")
	return service_names

# Преобразование ID услуг в список цен
def convert_service_ids_to_service_prices(yc: YClients, service_ids):
	services = yc.get_raw_services()
	service_prices = []
	for service in services:
		if int(service['id']) in service_ids:
			service_prices.append(service['price_max'])
	return service_prices