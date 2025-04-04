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
