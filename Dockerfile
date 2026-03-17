# Используем официальный slim-образ Python 3.14
FROM python:3.14-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей в контейнер
COPY requirements.txt ./

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения в контейнер
COPY . .

# Определяем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=config.settings


# Пробрасываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]