# Flask API Project

Это простое API на Flask с использованием PostgreSQL для управления сотрудниками. Проект включает функции авторизации, просмотра и создания сотрудников.

## Содержание

1. [Описание проекта](#описание-проекта)
2. [Требования](#требования)
3. [Установка](#установка)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Запуск приложения](#запуск-приложения)
6. [Использование API](#использование-api)
7. [Лицензия](#лицензия)

---

## Описание проекта

API предоставляет следующие функции:
- **Авторизация**: Получение токена для доступа к защищённым эндпоинтам.
- **Просмотр всех сотрудников**: Получение списка всех сотрудников.
- **Создание нового сотрудника**: Добавление нового сотрудника в базу данных.

---

## Требования

Для работы с проектом необходимо установить:
- Python 3.x
- PostgreSQL
- Git (для клонирования репозитория)

Также потребуются следующие Python-библиотеки:
- Flask
- psycopg2-binary
- python-dotenv
- requests

---

## Установка

1. Клонируй репозиторий:

   ```bash
   git clone https://github.com/kowa541/apishka.git
   cd apishka
2. Создай виртуальное окружение:
   ```bash
   python -m venv venv
3. Активируй виртуальное окружение:
  Для Windows:
  ```powershell
  .\venv\Scripts\Activate
  ```
  Для macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
4. Установи зависимости

# Настройка базы данных
1. Установи и запусти PostgreSQL.
  Создай базу данных:
 ```sql
CREATE DATABASE company_db;
 ```
Создай таблицы: 
 ```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    username VARCHAR(50) UNIQUE NOT NULL,
    has_email BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_fired BOOLEAN DEFAULT FALSE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

 ```
Добавь тестового пользователя:
 ```sql
INSERT INTO users (username, password) VALUES ('admin', 'password123');
 ```
Создай файл .env в корне проекта и добавь данные для подключения к базе данных:
DB_NAME=company_db
DB_USER=postgres
DB_PASSWORD=your_password 
DB_HOST=localhost
DB_PORT=5432
JIRA_API_TOKEN=your_jira_api_token
JIRA_URL=https://your-domain.atlassian.net
JIRA_ADMIN_EMAIL=your-admin@example.com

# Запуск приложения
Убедись, что PostgreSQL запущен.
Активируй виртуальное окружение (если оно не активировано):
```powershell
.\venv\Scripts\Activate
```
Запусти приложение:
```bash
python app.py
```
API будет доступно по адресу http://127.0.0.1:5000.

# Использование API POSTMAN
1. Авторизация
    POST /login
   
  Пример запроса:
json
{
    "username": "admin",
    "password": "password123"
}

  Пример ответа:
json
{
    "message": "Авторизация успешна",
    "token": "your-generated-token"
}

2. Просмотр всех сотрудников
GET /employees
Добавь заголовок:
Authorization: your-generated-token

Пример ответа:

json
 {
     "id": 1,
     "first_name": "Иван",
     "last_name": "Иванов",
     "middle_name": "Иванович",
     "username": "ivan_ivanov",
     "has_email": true,
     "created_at": "2023-10-01T12:34:56",
     "is_fired": false
 }

3. Создание нового сотрудника
POST /employees

Добавь заголовки:
Authorization: your-generated-token
Content-Type: application/json

Пример запроса:
{
    "first_name": "Петр",
    "last_name": "Петров",
    "middle_name": "Петрович",
    "username": "petr_petrov",
    "has_email": true,
    "is_fired": false
}

Пример ответа:
json
{
    "message": "Сотрудник успешно добавлен"
}

4.Создание учетной записи сотрудникв в Jira

POST /add/user/jira

Добавь заголовки:
Authorization: your-generated-token
Content-Type: application/json

Пример запроса:
{
    {
    "email": "test@test.com",
    "products": ["jira-software"]
    }
}

Пример ответа:
json
{
    "jira_data": {
        "accountId": "557058:f2e65aff-b01b-4c82-8edd-59a4cca0e96c",
        "accountType": "atlassian",
        "active": true,
        "applicationRoles": {
            "items": [],
            "size": 0
        },
        "avatarUrls": {
            "16x16": "https://secure.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-2.png",
            "24x24": "https://secure.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-2.png",
            "32x32": "https://secure.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-2.png",
            "48x48": "https://secure.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-2.png"
        },
        "displayName": "s",
        "emailAddress": "test@test.com",
        "expand": "groups,applicationRoles",
        "groups": {
            "items": [],
            "size": 0
        },
        "locale": "en_US",
        "self": "https://mlamps.atlassian.net/rest/api/3/user?accountId=557058:f2e65aff-b01b-4c82-8edd-59a4cca0e96c",
        "timeZone": "Asia/Yekaterinburg"
    },
    "message": "Пользователь успешно добавлен в Jira"
}

5.Блокировка пользователя в Jira

DELETE /block/user/jira

Добавь заголовки:
Authorization: your-generated-token

Пример запроса:
json
{
    "username": "blalagazc"
}

Пример ответа:
204 NO CONTENT
