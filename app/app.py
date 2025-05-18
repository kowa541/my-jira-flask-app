from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import os
import uuid  # Для генерации уникального токена
import json
import requests
from requests.auth import HTTPBasicAuth


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
    print(employees)
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

@app.route('/jira/auth', methods=["POST"])
def login_in_jira():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    JIRA_URL = os.getenv('JIRA_URL')
    API_TOKEN = os.getenv('JIRA_API_TOKEN')
    JIRA_ADMIN_EMAIL = os.getenv('JIRA_ADMIN_EMAIL')

    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"message": "Необходим username"}), 400

    try:
        # Проверка авторизации
        response = requests.get(
            f"{JIRA_URL}/rest/api/3/myself",
            auth=HTTPBasicAuth(username, API_TOKEN)
        )

        if response.status_code == 200:
            user_data = response.json()
            return jsonify({
                "message": "Авторизация успешна",
                "user": user_data
            }), 200
        else:
            return jsonify({
                "message": "Ошибка авторизации",
                "status_code": response.status_code,
                "error": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({
            "message": "Внутренняя ошибка сервера",
            "error": str(e)
        }), 500


@app.route('/add/user/jira', methods=["POST"])
def create_user_Jira():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    JIRA_URL = os.getenv('JIRA_URL')
    API_TOKEN = os.getenv('JIRA_API_TOKEN')
    JIRA_ADMIN_EMAIL = os.getenv('JIRA_ADMIN_EMAIL')

    data = request.get_json()
    email = data.get('email')
    name = data.get('name')  # Уникальное имя пользователя

    if not email or not name:
        return jsonify({"message": "Необходимы email и name"}), 400

    try:
        # Проверка существования пользователя
        search_response = requests.get(
            f"{JIRA_URL}/rest/api/3/user/search?query={name}",
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL, API_TOKEN)
        )

        if search_response.status_code == 200 and search_response.json():
            return jsonify({
                "message": "Пользователь уже существует",
                "existing_user": search_response.json()
            }), 409

        # Создание пользователя
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        user_data = json.dumps({
            "emailAddress": email,
            "name": name,
            "displayName": name
        })

        endpoint = "/rest/api/3/user"
        response = requests.post(
            f"{JIRA_URL}{endpoint}",
            headers=headers,
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL, API_TOKEN),
            data=user_data
        )

        if response.status_code == 201:
            return jsonify({
                "message": "Пользователь успешно добавлен в Jira",
                "jira_data": response.json()
            }), 201
        else:
            return jsonify({
                "message": "Ошибка при добавлении пользователя в Jira",
                "jira_error": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({
            "message": "Внутренняя ошибка сервера",
            "error": str(e)
        }), 500

@app.route('/block/user/jira', methods=['DELETE'])
def block_user_jira():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    JIRA_URL = os.getenv('JIRA_URL')
    API_TOKEN = os.getenv('JIRA_API_TOKEN')
    JIRA_ADMIN_EMAIL = os.getenv('JIRA_ADMIN_EMAIL')

    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"message": "Необходим username"}), 400

    try:
        # Поиск пользователя
        search_endpoint = "/rest/api/3/user/search"
        search_response = requests.get(
            f"{JIRA_URL}{search_endpoint}?query={username}",
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL, API_TOKEN)
        )

        if search_response.status_code != 200 or not search_response.json():
            return jsonify({
                "message": "Пользователь не найден",
                "error": search_response.text
            }), 404

        users = search_response.json()
        account_id = None
        for user in users:
            if user.get("displayName") == username:
                account_id = user.get("accountId")
                break

        if not account_id:
            return jsonify({"message": "Пользователь не найден"}), 404

        # Удаление пользователя
        delete_endpoint = f"/rest/api/3/user?accountId={account_id}"
        delete_response = requests.delete(
            f"{JIRA_URL}{delete_endpoint}",
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL, API_TOKEN)
        )

        if delete_response.status_code == 204:
            return jsonify({"message": "Пользователь успешно удален"}), 204
        else:
            return jsonify({
                "message": "Ошибка при удалении пользователя",
                "error": delete_response.text
            }), delete_response.status_code

    except Exception as e:
        return jsonify({
            "message": "Внутренняя ошибка сервера",
            "error": str(e)
        }), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)