from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import os
import uuid  # Для генерации уникального токена
import json
import requests
from paramiko.ssh_exception import AuthenticationException
from requests.auth import HTTPBasicAuth
import paramiko
import socket


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

# авторизация в jira тест так как нихуя не работет
@app.route('/jira/auth', methods=["POST"])
def login_in_jira():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    JIRA_URL = os.getenv('JIRA_URL')
    print(JIRA_URL)
    endpoint = '/rest/auth/1/session'
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    token = os.getenv("JIRA_ADMIN_SERVER_TOKEN")

    if not username or not password:
        return jsonify({"message": "Нужны и username, и password"}), 400

    response = requests.post(
        f"{JIRA_URL}{endpoint}",
        headers={"Content-Type": "application/json"},
        json={"username": username, "password": token}
    )

    if response.status_code == 200:
        session_data = response.json().get("session", {})
        return jsonify({
            "message": "Авторизация успешна",
            "session": session_data
        }), 200
    else:
        return jsonify({
            "message": "Ошибка авторизации",
            "status_code": response.status_code,
            "error": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text
        }), response.status_code


#4 Добавление пользователя в Jira
@app.route('/add/user/jira', methods=["POST"])
def create_user_Jira():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401

    JIRA_URL = os.getenv('JIRA_URL')
    API_TOKEN = os.getenv('JIRA_API_TOKEN')
    JIRA_ADMIN_EMAIL = os.getenv('JIRA_ADMIN_EMAIL')
    TOKEN = os.getenv("JIRA_ADMIN_SERVER_TOKEN")
    print(TOKEN)
    
    data = request.get_json()
    email = data.get('email')
    products = data.get('products')


    if not email:
        return jsonify({"message": "Необходимы email"}), 400

    try:
        # Отправка запроса к Jira API
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        user = json.dumps({
        "name": 'test',
        "emailAddress": email,
        # "products": products,
        # "applicationKeys": ["jira-core"]
        })
    
        endpoint = "/rest/api/2/user"
        response = requests.post(
            f"{JIRA_URL}{endpoint}",
            headers=headers,
            auth=HTTPBasicAuth(JIRA_ADMIN_EMAIL,TOKEN),
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
            #Все равно ничего не выводит бусть будет
            return jsonify({
                "message": "Пользователь успешно удалён",
            }), 204
        elif block_response.status_code == 400:
            return jsonify({
                "message": "Пользователь не может быть удалён",
                "error": block_response.text
            }), 400
        elif block_response.status_code == 403:
            return jsonify({
                "message": 'У вас недостаточно прав',
                "error": block_response.text
            }), 403
        
    except Exception as e:
        return jsonify({
            "message": "Внутренняя ошибка сервера",
            "error": str(e)
        }), 500

def get_ssh_server_connection(request):
    data = request.get_json()

    ssh_host = data.get('ssh_host')
    ssh_port = int(data.get('ssh_port'))
    ssh_user = data.get('ssh_user')
    ssh_passphrase = data.get('ssh_passphrase')

    if not ssh_host or not ssh_port or not ssh_user or not ssh_passphrase:
        return 400

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ssh_host, port=ssh_port, username=ssh_user, passphrase=ssh_passphrase, timeout=10)
    except AuthenticationException:
        return 401
    except socket.timeout:
        return 502

    return ssh

# Создание SSH-пользователя
@app.route('/add/user/ssh',methods=['POST'])
def create_user_shh():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401
    data = request.get_json()
    username = data.get('username')
    group = data.get('group')
    ssh = get_ssh_server_connection(request)

    if not username or not group:
        return jsonify({"message": "Недостаточно данных"}), 400

    match ssh:
        case 400:
            return jsonify({"message": "Недостаточно данных"}), 400
        case 401:
            return jsonify({"message": "Ошибка аутентификации SSH"}), 401
        case 502:
            return jsonify({"message": "Плохой шлюз"}), 502

    stdin, stdout, stderr = ssh.exec_command(f"getent group {group}")
    check_group = stdout.read().decode().strip() == ""

    if check_group:
        return jsonify({"message": "Указанная группа отсутствует"}), 404

    stdin, stdout, stderr = ssh.exec_command(f"id {username}")
    check_user = stdout.channel.recv_exit_status() == 0

    if check_user:
        return jsonify({"message": "Имя пользователя занято"}), 409

    commands = [
        f"sudo useradd -m {username}",
        f"sudo usermod -G {group} {username}"
    ]

    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode(), stderr.read().decode())

    ssh.close()

    return jsonify({"message":"SSH-Пользователь успешно добавлен"}), 201

# Добавление SSH-ключа
@app.route('/add/key/ssh',methods=['POST'])
def add_key_shh():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401
    data = request.get_json()
    username = data.get('username')
    pub_key = data.get('pub_key')
    ssh = get_ssh_server_connection(request)

    if not username or not pub_key:
        return jsonify({"message": "Недостаточно данных"}), 400

    match ssh:
        case 400:
            return jsonify({"message": "Недостаточно данных"}), 400
        case 401:
            return jsonify({"message": "Ошибка аутентификации SSH"}), 401
        case 502:
            return jsonify({"message": "Плохой шлюз"}), 502

    cmd = (f"mkdir -p /home/{username}/.ssh && echo '{pub_key}'"
           f" >> /home/{username}/.ssh/authorized_keys"
           f" && chown -R {username}:{username} /home/{username}/.ssh")
    ssh.exec_command(cmd)

    ssh.close()

    return jsonify({"message": "SSH-ключ успешно добавлен"}), 201

# Список учетных записей SSH на хосте
@app.route('/get/users/ssh',methods=['GET'])
def get_users_ssh():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401
    ssh = get_ssh_server_connection(request)

    match ssh:
        case 400:
            return jsonify({"message": "Недостаточно данных"}), 400
        case 401:
            return jsonify({"message": "Ошибка аутентификации SSH"}), 401
        case 502:
            return  jsonify({"message": "Плохой шлюз"}), 502

    stdin, stdout, stderr = ssh.exec_command("cat /etc/passwd | cut -d: -f1")
    users = stdout.read().decode().splitlines()

    ssh.close()

    return jsonify(users), 200

# Список агентов
@app.route('/get/agents/ssh',methods=['GET'])
def get_agents_ssh():
    if not check_token(request):
        return jsonify({"message": "Необходима авторизация"}), 401
    ssh = get_ssh_server_connection(request)

    match ssh:
        case 400:
            return jsonify({"message": "Недостаточно данных"}), 400
        case 401:
            return jsonify({"message": "Ошибка аутентификации SSH"}), 401
        case 502:
            return jsonify({"message": "Плохой шлюз"}), 502

    cmd = "ssh-add -l"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    agents = stdout.read().decode().splitlines()

    ssh.close()

    return jsonify(agents), 200

if __name__ == '__main__':
    app.run(debug=True)