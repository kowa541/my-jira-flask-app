# Базовый образ Python
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY app/requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY app/ .

# Команда для запуска приложения
CMD ["python", "app.py"]