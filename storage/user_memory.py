import sqlite3
from datetime import datetime

DB_PATH = "storage/user_memory.db"

# Создание таблицы, если не существует
def init_db():
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			user_id INTEGER PRIMARY KEY,
			phone TEXT,
			name TEXT,
			last_visit TEXT,
			first_name TEXT,
			last_name TEXT,
			middle_name TEXT,
			email TEXT
		)
	''')
	conn.commit()
	conn.close()

# Сохранить или обновить базовые данные пользователя
def remember_user(user_id: int, phone: str = None, name: str = None, last_visit: str = None):
	init_db()
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
	exists = cursor.fetchone()

	if not last_visit:
		last_visit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	if exists:
		cursor.execute("""
			UPDATE users SET
				phone = COALESCE(?, phone),
				name = COALESCE(?, name),
				last_visit = ?
			WHERE user_id = ?
		""", (phone, name, last_visit, user_id))
	else:
		cursor.execute("""
			INSERT INTO users (user_id, phone, name, last_visit)
			VALUES (?, ?, ?, ?)
		""", (user_id, phone, name, last_visit))

	conn.commit()
	conn.close()

# Получить базовые данные пользователя по ID
def get_user_data(user_id: int):
	init_db()
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	cursor.execute("SELECT phone, name, last_visit FROM users WHERE user_id = ?", (user_id,))
	row = cursor.fetchone()
	conn.close()
	if row:
		return {"phone": row[0], "name": row[1], "last_visit": row[2]}
	return {}

# Сохранить расширенный профиль пользователя
def remember_user_profile(
		user_id: int, 
		first_name=None, 
		last_name=None, 
		middle_name=None, 
		phone=None, 
		email=None
	):
	init_db()
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
	exists = cursor.fetchone()

	if exists:
		cursor.execute("""
			UPDATE users SET
				first_name = ?,
				last_name = ?,
				middle_name = ?,
				phone = ?,
				email = ?
			WHERE user_id = ?
		""", (first_name, last_name, middle_name, phone, email, user_id))
	else:
		cursor.execute("""
			INSERT INTO users (user_id, first_name, last_name, middle_name, phone, email)
			VALUES (?, ?, ?, ?, ?, ?)
		""", (user_id, first_name, last_name, middle_name, phone, email))
	conn.commit()
	conn.close()

# Получить расширенный профиль пользователя
def get_user_profile(user_id: int):
	init_db()
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, middle_name, phone, email FROM users WHERE user_id = ?", (user_id,))
	row = cursor.fetchone()
	conn.close()
	if row:
		return {
			"first_name": row[0],
			"last_name": row[1],
			"middle_name": row[2],
			"phone": row[3],
			"email": row[4]
		}
	return {}