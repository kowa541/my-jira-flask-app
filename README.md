# API Onboarding

Это приложение на Flask, которое интегрируется с Jira, SSH и PostgreSQL через Docker.

## Содержание
- [Описание](#описание)
- [Требования](#требования)
- [Установка](#установка)
- [Запуск](#запуск)
- [API Endpoints](#api-endpoints)
- [Лицензия](#лицензия)

---

## Описание

Это приложение предоставляет REST API для работы с Jira, SSH и базой данных PostgreSQL. Оно позволяет:

●	Авторизация для старта программы;
●	Просмотр всех сотрудников;
●	Создание сотрудника;
●	Создание пользователя в Jira;
●	Блокировка пользователя в Jira;
●	Создание SSH-пользователя;
●	Добавление SSH-ключа;
●	Получение списка серверов;
●	Список учетных записей SSH на хосте;
●	Список агентов;


---

## Требования

Для запуска проекта вам понадобятся:
- Docker и Docker Compose
- Python 3.8+
- База данных PostgreSQL
- Аккаунт Jira с правами администратора
- SSH сервер с пользователем имеющий права sudo с приватным ключом от пользователя на запускаемой машине

---

## Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/your-username/my-jira-flask-app.git
   cd my-jira-flask-app
2. Добавьте файл .env
   DB_NAME=company_db
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=db
   DB_PORT=5432
   JIRA_URL=http://jira:8080
   JIRA_ADMIN_EMAIL=your-email
   JIRA_API_TOKEN=your_api_token_here
   
3. Запуск
   Запуск через Docker:
      docker-compose up --build
   После запуска:
      Flask будет доступен на http://localhost:5000.
      Jira будет доступна на http://localhost:8080.
   Остановка контейнеров:
      docker-compose down


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

6. Создание SSH-пользователя
    
POST /add/user/ssh

Добавь заголовки:
Authorization: your-generated-token

Пример запроса:
json
{
    "username": "dummy",
    "group": "read",
    "ssh_host": "localhost",
    "ssh_port": "22",
    "ssh_user": "root",
    "ssh_passphrase": "test"
}

Пример ответа:
json
{
    "message": "SSH-Пользователь успешно добавлен"
}

7. Добавление SSH-ключа

POST /add/key/ssh

Добавь заголовки:
Authorization: your-generated-token

Пример запроса:
json
{
    "username": "dummy",
    "pub_key": "<your_ssh_public_key>",
    "ssh_host": "localhost",
    "ssh_port": "22",
    "ssh_user": "root",
    "ssh_passphrase": "test"
}

Пример ответа:
json
{
    "message": "SSH-ключ успешно добавлен"
}

8. Список учетных записей SSH на хосте

GET /get/users/ssh

Добавь заголовки:
Authorization: your-generated-token

Пример запроса:
json
{
    "ssh_host": "localhost",
    "ssh_port": "22",
    "ssh_user": "root",
    "ssh_passphrase": "test"
}

Пример ответа:

json
{
    [
        "root",
        "dummy"
    ]
}

9. Список агентов

GET /get/agents/ssh

Добавь заголовки:
Authorization: your-generated-token

Пример запроса:
json
{
    "ssh_host": "localhost",
    "ssh_port": "22",
    "ssh_user": "root",
    "ssh_passphrase": "test"
}

Пример ответа:

json
{
    [
    ]
}

10. Список серверов

GET /get/servers/ssh

Добавь заголовки:
Authorization: your-generated-token

Пример ответа:

json
{
    "id": 1,
    "ip": "0.0.0.0",
    "port": "5555"
}

