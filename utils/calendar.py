# utils/calendar.py
from datetime import datetime, timedelta, timezone
from io import BytesIO
from aiogram.types import InputFile
import urllib.parse

# Генерация ссылки на Google Календарь
def generate_calendar_url(service_title, company, address, staff_name, phones, dt_start_obj, dt_end_obj):
	start_str = dt_start_obj.astimezone(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
	end_str = dt_end_obj.astimezone(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
	return "https://calendar.google.com/calendar/u/0/r/eventedit?" + urllib.parse.urlencode({
		"text": f"{service_title} - {company.get('public_title', '')} на {address}",
		"dates": f"{start_str}/{end_str}",
		"details": f"{company.get('public_title', '')}\n{company.get('country', '')} {company.get('city', '')} {address}\n\n{service_title}\nСпециалист: {staff_name}\nТелефоны: {' '.join(phones)}\n\nСайт: {company.get('site', '')}",
		"location": f"{company.get('country', '')} {company.get('city', '')} {address}"
	})

# Генерация .ics-файла в памяти
def generate_ics_file(service_title, company, address, staff_name, phones, dt_start_obj, dt_end_obj):
	start_str = dt_start_obj.strftime("%Y%m%dT%H%M%SZ")
	end_str = dt_end_obj.strftime("%Y%m%dT%H%M%SZ")
	ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{service_title} - {company.get('public_title', '')}
DTSTART:{start_str}
DTEND:{end_str}
DESCRIPTION:{company.get('public_title', '')}\n{company.get('country', '')} {company.get('city', '')} {address}\n\n{service_title}\nСпециалист: {staff_name}\nТелефоны: {' '.join(phones)}\n\nСайт: {company.get('site', '')}
LOCATION:{company.get('country', '')} {company.get('city', '')} {address}
END:VEVENT
END:VCALENDAR"""
	ics_io = BytesIO(ics_content.encode("utf-8"))
	return InputFile(ics_io, filename="zapic.ics")