# Система управления курсами и уроками

Django REST Framework приложение для управления образовательными курсами и уроками с JWT-авторизацией и системой прав доступа.

## Описание проекта

Проект представляет собой REST API для платформы онлайн-обучения с возможностью:
- Регистрации и аутентификации пользователей через JWT
- Управления курсами и уроками (CRUD операции)
- Разграничения прав доступа между обычными пользователями и модераторами
- Отслеживания платежей пользователей

## Технологии

- Python 3.x
- Django 6.0.2
- Django REST Framework 3.16.1
- Django REST Framework SimpleJWT 5.5.1
- PostgreSQL
- django-filter 25.1

## Установка и запуск

### Вариант 1: Запуск через Docker Compose (рекомендуется)

#### 1. Клонирование репозитория
```bash
git clone <url-репозитория>
cd Viewsets@Generics
```

#### 2. Настройка переменных окружения
Скопируйте файл `.env.sample` в `.env` и заполните необходимые значения:
```bash
cp .env.sample .env
```

Минимально необходимые переменные:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# База данных (для docker-compose можно оставить значения по умолчанию)
NAME=viewsets_and_generics
DB_USER=postgres
PASSWORD=Qwerty123
HOST=db
PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Stripe (опционально)
STRIPE_SECRET_KEY=your-stripe-key

# Email (опционально)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### 3. Запуск проекта
```bash
docker-compose up -d --build
```

#### 4. Применение миграций
```bash
docker-compose exec web python manage.py migrate
```

#### 5. Создание группы модераторов
```bash
docker-compose exec web python manage.py create_groups
```

#### 6. Создание суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```

#### 7. Проверка работоспособности сервисов

**Веб-сервер Django:**
```bash
# Проверка логов
docker-compose logs web

# Проверка доступности API
curl http://localhost:8000/materials/courses/
```
Ожидаемый результат: JSON-ответ с данными о курсах или сообщение об авторизации.

**База данных PostgreSQL:**
```bash
# Проверка статуса контейнера
docker-compose ps db

# Подключение к базе данных
docker-compose exec db psql -U postgres -d viewsets_and_generics -c "\dt"
```
Ожидаемый результат: список таблиц Django приложения.

**Redis:**
```bash
# Проверка статуса
docker-compose ps redis

# Проверка подключения
docker-compose exec redis redis-cli ping
```
Ожидаемый результат: `PONG`

**Celery Worker:**
```bash
# Проверка логов
docker-compose logs celery

# Проверка активных воркеров
docker-compose exec celery celery -A config inspect active
```
Ожидаемый результат: информация о работающих задачах или пустой список.

**Celery Beat:**
```bash
# Проверка логов
docker-compose logs celery-beat

# Проверка зарегистрированных задач
docker-compose exec celery-beat celery -A config inspect registered
```
Ожидаемый результат: список зарегистрированных периодических задач.

#### 8. Остановка сервисов
```bash
# Остановка без удаления контейнеров
docker-compose stop

# Остановка с удалением контейнеров
docker-compose down

# Остановка с удалением контейнеров и volumes (ВНИМАНИЕ: удалит данные БД!)
docker-compose down -v
```

### Вариант 2: Локальный запуск (без Docker)

#### 1. Клонирование репозитория
```bash
git clone <url-репозитория>
cd Viewsets@Generics
```

#### 2. Создание виртуального окружения
```bash
python -m venv .venv
.venv\Scripts\activate  # для Windows
source .venv/bin/activate  # для Linux/Mac
```

#### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 4. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
SECRET_KEY=your-secret-key
NAME=database_name
DB_USER=database_user
PASSWORD=database_password
HOST=localhost
PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Требования:**
- PostgreSQL должен быть установлен и запущен
- Redis должен быть установлен и запущен

#### 5. Применение миграций
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Создание группы модераторов
```bash
python manage.py create_groups
```

#### 7. Создание суперпользователя
```bash
python manage.py createsuperuser
```

#### 8. Запуск сервисов

Вам потребуется 3 отдельных терминала:

**Терминал 1 - Django сервер:**
```bash
python manage.py runserver
```

**Терминал 2 - Celery Worker:**
```bash
celery -A config worker --pool=solo -l info  # для Windows
celery -A config worker -l info              # для Linux/Mac
```

**Терминал 3 - Celery Beat:**
```bash
celery -A config beat -l info
```

## Структура API

### Аутентификация

#### Регистрация пользователя
```
POST /users/users/
```
Тело запроса:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "phone": "+7999999999",
  "tg_nick": "@username"
}
```

#### Получение JWT токена
```
POST /users/token/
```
Тело запроса:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Обновление токена
```
POST /users/token/refresh/
```
Тело запроса:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Пользователи

Все эндпоинты требуют авторизации (кроме регистрации).

```
GET    /users/users/           # Список пользователей
GET    /users/users/{id}/      # Профиль пользователя
PUT    /users/users/{id}/      # Обновление своего профиля
PATCH  /users/users/{id}/      # Частичное обновление своего профиля
DELETE /users/users/{id}/      # Удаление своего профиля
```

**Заголовок авторизации:**
```
Authorization: Bearer <access_token>
```

### Курсы

```
GET    /materials/courses/           # Список курсов
POST   /materials/courses/           # Создание курса (только не-модераторы)
GET    /materials/courses/{id}/      # Детали курса
PUT    /materials/courses/{id}/      # Обновление курса (модераторы или владелец)
PATCH  /materials/courses/{id}/      # Частичное обновление курса
DELETE /materials/courses/{id}/      # Удаление курса (только владелец)
```

Пример создания курса:
```json
{
  "name": "Python для начинающих",
  "description": "Базовый курс по Python",
  "preview": null
}
```

### Уроки

```
GET    /materials/lessons/                # Список уроков
POST   /materials/lessons/create/         # Создание урока (только не-модераторы)
GET    /materials/lessons/{id}/           # Детали урока
PUT    /materials/lessons/{id}/update/    # Обновление урока (модераторы или владелец)
PATCH  /materials/lessons/{id}/update/    # Частичное обновление урока
DELETE /materials/lessons/{id}/delete/    # Удаление урока (только владелец)
```

Пример создания урока:
```json
{
  "name": "Введение в Python",
  "description": "Первый урок курса",
  "course": 1,
  "video_url": "https://youtube.com/watch?v=..."
}
```

### Платежи

```
GET /users/payments/  # Список платежей с фильтрацией
```

Параметры фильтрации:
- `course` - фильтр по курсу
- `lesson` - фильтр по уроку
- `payment_method` - фильтр по способу оплаты (cash/transfer)
- `ordering` - сортировка по дате (`payment_date` или `-payment_date`)

## Система прав доступа

### Роли пользователей

#### 1. Обычный пользователь
- Может создавать курсы и уроки
- Может просматривать все курсы и уроки
- Может редактировать и удалять **только свои** курсы и уроки
- Может просматривать любой профиль (без чувствительных данных)
- Может редактировать только свой профиль

#### 2. Модератор
- **НЕ может** создавать курсы и уроки
- Может просматривать все курсы и уроки
- Может редактировать **любые** курсы и уроки
- **НЕ может** удалять курсы и уроки
- Назначается через админ-панель

### Назначение модераторов

1. Войдите в админ-панель: `http://localhost:8000/admin/`
2. Перейдите в раздел **Users**
3. Выберите пользователя
4. В разделе **Groups** добавьте группу **"Модераторы"**
5. Сохраните изменения

### Права доступа к профилям

- **Просмотр чужого профиля**: доступна только общая информация (email, имя, телефон, telegram, аватар)
- **Просмотр своего профиля**: доступна вся информация, включая фамилию и историю платежей
- **Редактирование**: только свой профиль

## Примеры использования

### Пример работы с API

#### 1. Регистрация
```bash
curl -X POST http://localhost:8000/users/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "securepass123",
    "first_name": "Иван"
  }'
```

#### 2. Получение токена
```bash
curl -X POST http://localhost:8000/users/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "securepass123"
  }'
```

#### 3. Создание курса
```bash
curl -X POST http://localhost:8000/materials/courses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ваш_токен>" \
  -d '{
    "name": "Django REST Framework",
    "description": "Полный курс по DRF"
  }'
```

#### 4. Получение списка курсов
```bash
curl -X GET http://localhost:8000/materials/courses/ \
  -H "Authorization: Bearer <ваш_токен>"
```

## Структура проекта

```
Viewsets@Generics/
├── congig/                     # Настройки проекта
│   ├── settings.py            # Основные настройки Django
│   ├── urls.py                # Главный роутинг
│   └── ...
├── materials/                  # Приложение для курсов и уроков
│   ├── models.py              # Модели Course и Lesson
│   ├── serializer.py          # Сериализаторы
│   ├── views.py               # ViewSet и Generic views
│   ├── urls.py                # Маршруты для materials
│   └── ...
├── users/                      # Приложение пользователей
│   ├── models.py              # Модели User и Payment
│   ├── serializers.py         # Сериализаторы пользователей
│   ├── views.py               # ViewSet для пользователей
│   ├── permissions.py         # Кастомные права доступа
│   ├── urls.py                # Маршруты для users
│   └── management/
│       └── commands/
│           └── create_groups.py  # Команда создания группы модераторов
├── .env                        # Переменные окружения (не в Git)
├── requirements.txt            # Зависимости проекта
├── manage.py                   # Django CLI
└── Readme.md                   # Документация
```

## Модели данных

### User (Пользователь)
- `email` - email (используется для входа)
- `password` - хэшированный пароль
- `first_name` - имя
- `last_name` - фамилия
- `phone` - телефон
- `tg_nick` - Telegram никнейм
- `avatar` - аватар

### Course (Курс)
- `name` - название курса
- `description` - описание
- `preview` - превью изображение
- `owner` - владелец курса (ForeignKey к User)

### Lesson (Урок)
- `name` - название урока
- `description` - описание
- `course` - курс (ForeignKey к Course)
- `preview` - превью изображение
- `video_url` - ссылка на видео
- `owner` - владелец урока (ForeignKey к User)

### Payment (Платеж)
- `user` - пользователь (ForeignKey к User)
- `payment_date` - дата и время оплаты
- `course` - оплаченный курс (ForeignKey к Course, опционально)
- `lesson` - оплаченный урок (ForeignKey к Lesson, опционально)
- `amount` - сумма оплаты
- `payment_method` - способ оплаты (cash/transfer)

## Безопасность

- Все пароли хэшируются через `make_password()`
- JWT токены с истечением срока действия (60 минут для access, 1 день для refresh)
- Пароли никогда не возвращаются в API ответах
- CSRF защита включена
- Требуется авторизация для всех эндпоинтов (кроме регистрации и получения токенов)

## Тестирование

Для тестирования API рекомендуется использовать:
- **Postman** - GUI клиент для тестирования API
- **curl** - командная строка
- **Django REST Framework Browsable API** - встроенный веб-интерфейс

## Возможные ошибки и решения

### 401 Unauthorized
- Проверьте, что токен добавлен в заголовок `Authorization: Bearer <token>`
- Проверьте срок действия токена (обновите через `/users/token/refresh/`)

### 403 Forbidden
- Проверьте права доступа пользователя
- Убедитесь, что пытаетесь редактировать свой объект или являетесь модератором

### 404 Not Found
- Проверьте правильность URL
- Убедитесь, что объект существует в базе данных

## Разработка

### Создание миграций после изменения моделей
```bash
python manage.py makemigrations
python manage.py migrate
```

### Запуск в режиме разработки
```bash
python manage.py runserver
```

### Создание тестовых данных
Используйте админ-панель Django или Django shell:
```bash
python manage.py shell
```

## Настройка удаленного сервера и деплой

### Подготовка сервера

#### 1. Требования к серверу
- Ubuntu 20.04 или новее
- Docker и Docker Compose установлены
- Открыты порты: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Минимум 2GB RAM

#### 2. Установка Docker на сервере
```bash
# Обновление пакетов
sudo apt update
sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose -y

# Проверка установки
docker --version
docker-compose --version
```

#### 3. Настройка SSH для деплоя
```bash
# На локальной машине: генерация SSH ключа (если еще не создан)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Копирование публичного ключа на сервер
ssh-copy-id user@your_server_ip

# Проверка подключения
ssh user@your_server_ip
```

#### 4. Подготовка каталога на сервере
```bash
# На сервере
mkdir -p ~/app
cd ~/app
```

### Настройка GitHub Actions для автоматического деплоя

#### 1. Добавление GitHub Secrets
В вашем репозитории GitHub перейдите в Settings → Secrets and variables → Actions и добавьте следующие секреты:

**Обязательные секреты:**
- `SERVER_HOST` - IP-адрес или домен вашего сервера
- `SERVER_USER` - имя пользователя на сервере
- `SSH_PRIVATE_KEY` - приватный SSH ключ для подключения к серверу
- `DOCKER_USERNAME` - имя пользователя Docker Hub
- `DOCKER_PASSWORD` - токен доступа Docker Hub

**Секреты для приложения (передаются в контейнер):**
- `SECRET_KEY` - Django SECRET_KEY
- `DB_NAME` - название базы данных
- `DB_USER` - пользователь базы данных
- `DB_PASSWORD` - пароль базы данных
- `STRIPE_SECRET_KEY` - ключ Stripe API (опционально)
- `EMAIL_HOST_USER` - email для отправки (опционально)
- `EMAIL_HOST_PASSWORD` - пароль от email (опционально)

#### 2. Создание Docker Hub репозитория
```bash
# Авторизация в Docker Hub
docker login

# Создайте публичный или приватный репозиторий на https://hub.docker.com/
# Название репозитория: <ваш_username>/viewsets-generics
```

#### 3. Структура workflow файла
Workflow файл должен находиться в `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Server

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/viewsets-generics:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/viewsets-generics:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/app
            docker-compose pull
            docker-compose up -d --force-recreate
            docker-compose exec -T web python manage.py migrate
```

### Процесс деплоя

#### Автоматический деплой через GitHub Actions

**Шаг 1: Подготовка кода**
```bash
# Убедитесь, что все изменения зафиксированы
git status
git add .
git commit -m "Deploy: описание изменений"
```

**Шаг 2: Отправка в репозиторий**
```bash
# Отправка в главную ветку (main)
git push origin main
```

**Шаг 3: Мониторинг деплоя**
1. Перейдите в GitHub → вкладка Actions
2. Найдите запущенный workflow "Deploy to Server"
3. Отслеживайте выполнение каждого шага:
   - `build-and-push` - сборка и отправка Docker образа
   - `deploy` - деплой на сервер

**Шаг 4: Проверка на сервере**
```bash
# Подключитесь к серверу
ssh user@your_server_ip

# Проверьте статус контейнеров
cd ~/app
docker-compose ps

# Проверьте логи
docker-compose logs web
docker-compose logs db
docker-compose logs celery

# Проверьте доступность API
curl http://localhost:8000/materials/courses/
```

#### Ручной деплой (без GitHub Actions)

**Шаг 1: Сборка образа локально**
```bash
docker build -t your_username/viewsets-generics:latest .
docker push your_username/viewsets-generics:latest
```

**Шаг 2: Копирование файлов на сервер**
```bash
# Копирование docker-compose.yml и .env
scp docker-compose.yml user@your_server_ip:~/app/
scp .env user@your_server_ip:~/app/
```

**Шаг 3: Запуск на сервере**
```bash
# Подключение к серверу
ssh user@your_server_ip

# Переход в директорию приложения
cd ~/app

# Получение последнего образа
docker-compose pull

# Запуск контейнеров
docker-compose up -d

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание группы модераторов
docker-compose exec web python manage.py create_groups
```

### Управление деплоем

#### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f web
docker-compose logs -f celery

# Последние 100 строк
docker-compose logs --tail=100 web
```

#### Перезапуск сервисов
```bash
# Перезапуск всех сервисов
docker-compose restart

# Перезапуск конкретного сервиса
docker-compose restart web
docker-compose restart celery
```

#### Обновление приложения
```bash
# Получение новой версии образа
docker-compose pull

# Пересоздание контейнеров
docker-compose up -d --force-recreate

# Применение новых миграций
docker-compose exec web python manage.py migrate
```

#### Откат к предыдущей версии
```bash
# Остановка текущих контейнеров
docker-compose down

# Запуск конкретной версии образа
# Измените в docker-compose.yml: image: username/viewsets-generics:previous_tag
docker-compose up -d
```

### Мониторинг и обслуживание

#### Проверка использования ресурсов
```bash
# Использование Docker
docker stats

# Использование диска
df -h
docker system df

# Очистка неиспользуемых образов и контейнеров
docker system prune -a
```

#### Резервное копирование базы данных
```bash
# Создание резервной копии
docker-compose exec db pg_dump -U postgres viewsets_and_generics > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из резервной копии
docker-compose exec -T db psql -U postgres viewsets_and_generics < backup_20260324_120000.sql
```

### Настройка домена и HTTPS (опционально)

#### 1. Настройка DNS
Добавьте A-запись в настройках вашего домена:
```
A record: @ → your_server_ip
A record: www → your_server_ip
```

#### 2. Установка Nginx и Certbot
```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

#### 3. Настройка Nginx
Создайте файл `/etc/nginx/sites-available/viewsets`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/viewsets /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Получение SSL сертификата
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Лицензия

Учебный проект

## Автор

Создано в рамках выполнения домашнего задания
