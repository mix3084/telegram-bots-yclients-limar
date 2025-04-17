# texts/templates.py

# Шаблоны текстов сообщений и меню
class BasicMessages:
	main_menu_template = """
Запись на прием:

👤 Специалист: *{staff_name}*
📅 Дата и время: *{day_and_time}*

🔧 Услуги:
*{service_names}*

=============

💵 Итого: {price} ₽
	"""

# Формирование текста главного меню на основе данных
def prepare_main_menu_template(staff_name = "", day_name = "", time = "", service_names = "", service_prices = []):
	if not staff_name:
		staff_name = "Не выбран"
	if not day_name:
		day_and_time = "Не выбраны"
	else:
		day_and_time = f"{day_name} в {time}"
	if not service_names:
		service_names = "Не выбраны"
	else:
		service_names = "\n".join(service_names)

	price = sum(service_prices) if service_prices else 0

	return BasicMessages.main_menu_template.format(
		staff_name=staff_name,
		day_and_time=day_and_time,
		service_names=service_names,
		price=str(price)
	)
