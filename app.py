from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import os
import uuid  # Для генерации уникального токена

# Загружаем переменные окружения из файла .env
load_dotenv()

app = Flask(__name__)

# Словарь для хранения активных токенов (в реальном проекте лучше использовать базу данных)
active_tokens = {}

# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

# 1. Авторизация
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        # Генерируем уникальный токен
        token = str(uuid.uuid4())
        active_tokens[token] = username  # Сохраняем токен
        return jsonify({"message": "Авторизация успешна", "token": token}), 200
    else:
        return jsonify({"message": "Неверный логин или пароль"}), 401

# Проверка токена
def check_token(request):
    token = request.headers.get('Authorization')
    if not token or token not in active_tokens:
        return False
    return True

# 2. Просмотр всех сотрудников
@app.route('/employees', methods=['GET'])
def get_employees():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()

    # Преобразуем результат в список словарей
    employees_list = []
    for employee in employees:
        employees_list.append({
            "id": employee[0],
            "first_name": employee[1],
            "last_name": employee[2],
            "middle_name": employee[3],
            "username": employee[4],
            "has_email": employee[5],
            "created_at": employee[6].isoformat(),  # Преобразуем дату в строку
            "is_fired": employee[7]
        })

    return jsonify(employees_list), 200

# 3. Создание нового сотрудника
@app.route('/employees', methods=['POST'])
def create_employee():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    middle_name = data.get('middle_name')
    username = data.get('username')
    has_email = data.get('has_email', False)  # По умолчанию False
    is_fired = data.get('is_fired', False)  # По умолчанию False

    # Проверка обязательных полей
    if not first_name or not last_name or not username:
        return jsonify({"message": "Недостаточно данных"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (first_name, last_name, middle_name, username, has_email, is_fired)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (first_name, last_name, middle_name, username, has_email, is_fired))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Сотрудник успешно добавлен"}), 201

if __name__ == '__main__':
    app.run(debug=True)