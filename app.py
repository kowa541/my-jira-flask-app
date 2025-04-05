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

#4 Добавление пользователя в Jira
@app.route('/add/user/jira', methods=["POST"])
def create_user_Jira():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    JIRA_URL = os.getenv('JIRA_URL')
    API_TOKEN = os.getenv('JIRA_API_TOKEN')
    JIRA_ADMIN_EMAIL = os.getenv('JIRA_ADMIN_EMAIL')
    
    data = request.get_json()
    email = data.get('email')
    products = data.get('products')


    if not email:
        return jsonify({"message": "Необходимы email и display_name"}), 400

    try:
        # Отправка запроса к Jira API
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        user = json.dumps({
        "emailAddress": email,
        "products": products,
        })
    
        endpoint = "/rest/api/3/user"
        response = requests.post(
            f"{JIRA_URL}{endpoint}",
            headers=headers,
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL, API_TOKEN),
            data=user
        )

        # Обработка ответа от Jira
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


#5 блоикровка сотрудника в jira
@app.route('/block/user/jira',methods=['DELETE'])
def block_user_jira():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    JIRA_URL = os.getenv('JIRA_URL')
    API_TOKEN = os.getenv('JIRA_API_TOKEN')
    JIRA_ADMIN_EMAIL = os.getenv('JIRA_ADMIN_EMAIL')
    blcok_endpoint = '/rest/api/3/user'
    search_endpoint = '/rest/api/3/user/search'
    headers = {
        "Accept": "application/json"
    }
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({"message": "Необходим username"}), 400
    try:

        search_response = requests.get(
            f"{JIRA_URL}{search_endpoint}?query={username}",
            headers=headers,
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL,API_TOKEN)
        )

        if search_response.status_code != 200 or not search_response.json():
            return jsonify({
                "message": "Пользователь не найден",
                "error": search_response.text
            }), 404

        print(search_response.json())
        for i in search_response.json():
            for j in i:
                if j == 'displayName':
                    if i[j] == username:
                        accountId = i['accountId']
                        break
        print(accountId)

        query = {
            'accountId': accountId
        }
        
        block_response = requests.delete(
            f'{JIRA_URL}{blcok_endpoint}',
            params=query,
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL,API_TOKEN)
        )

        if block_response.status_code == 204:
            return jsonify({
                "message": "Пользователь успешно удалён"
            }), 204
        elif block_response.status_code == 400:
            return jsonify({
                "message": "Пользователь не может быть удалён",
                "error": block_response.text
            }), 400
        elif block_response.status_code == 403:
            return jsonify({
                "message": 'У вас недостаточно прав',
                "eror": block_response.text
            }), 403
        
    except Exception as e:
        return jsonify({
            "message": "Внутренняя ошибка сервера",
            "error": str(e)
        }), 500
if __name__ == '__main__':
    app.run(debug=True)