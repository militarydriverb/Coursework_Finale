# Coursework Finale — Online Learning Platform

**Развёрнутое приложение:** http://158.160.243.163

REST API для платформы онлайн-обучения с JWT-авторизацией, асинхронными задачами и оплатой через Stripe.

## Технологии

- **Backend**: Python 3.12, Django 6, Django REST Framework
- **База данных**: PostgreSQL 18
- **Кеш / Брокер**: Redis 7
- **Очереди**: Celery + Celery Beat
- **Веб-сервер**: Gunicorn + Nginx
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Оплата**: Stripe

---

## Локальный запуск

### 1. Клонировать репозиторий

```bash
git clone <url-репозитория>
cd Coursework_Finale
```

### 2. Создать файл окружения

```bash
cp .env.sample .env
```

Заполнить `.env` (минимум для локального запуска):

```env
SECRET_KEY=любая-строка-для-разработки
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=coursework_finale
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
HOST=db
PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 3. Запустить все сервисы одной командой

```bash
docker compose up --build
```

При первом запуске автоматически выполнятся:
- миграции базы данных
- сборка статических файлов
- запуск всех контейнеров (web, db, redis, celery, celery-beat, nginx)

**Приложение доступно на `http://localhost`**

| URL | Описание |
|-----|----------|
| `http://localhost/` | API |
| `http://localhost/admin/` | Панель администратора |
| `http://localhost/swagger/` | Swagger UI |
| `http://localhost/redoc/` | ReDoc |

### Остановить проект

```bash
docker compose down
```

Остановить и удалить данные БД:

```bash
docker compose down -v
```

---

## Архитектура контейнеров

```
Клиент
  │
  ▼
Nginx (порт 80)
  ├── /static/  →  отдаёт статику напрямую
  ├── /media/   →  отдаёт медиафайлы напрямую
  └── /         →  проксирует в Gunicorn
                        │
                        ▼
                   Django + Gunicorn (порт 8000)
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
         PostgreSQL             Redis
                                   │
                        ┌──────────┤
                        ▼          ▼
                  Celery Worker  Celery Beat
```

---

## Настройка CI/CD и деплоя на сервер

### Схема веток

```
feature/* → develop (staging)
develop   → main    (production)
```

- Push в `develop` → автодеплой на staging-сервер
- Push в `main` → автодеплой на production-сервер

### GitHub Secrets

Перейти в репозиторий → **Settings → Secrets and variables → Actions** и добавить:

| Secret | Описание |
|--------|----------|
| `SECRET_KEY` | Django SECRET_KEY (для тестов) |
| `POSTGRES_PASSWORD` | Пароль БД (для тестов) |
| `DOCKER_USERNAME` | Логин Docker Hub |
| `DOCKER_PASSWORD` | Пароль / Access Token Docker Hub |
| `SSH_KEY` | Приватный SSH-ключ для доступа к серверам |
| `SSH_USER` | Пользователь на production сервере |
| `SERVER_IP` | IP production сервера |
| `SERVER_APP_DIR` | Путь к проекту на production (например `/home/user/coursework_finale`) |
| `STAGING_SSH_USER` | Пользователь на staging сервере |
| `STAGING_SERVER_IP` | IP staging сервера |
| `STAGING_SERVER_APP_DIR` | Путь к проекту на staging |

### GitHub Environments

Перейти в репозиторий → **Settings → Environments** и создать два окружения:
- `staging`
- `production`

Опционально: для `production` включить **Required reviewers** — тогда деплой потребует ручного подтверждения.

---

## Подготовка сервера

Выполнить на каждом сервере (production и staging).

### 1. Установить Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Установить Docker Compose

```bash
sudo apt-get install docker-compose-plugin
docker compose version
```

### 3. Настроить SSH-доступ для GitHub Actions

На локальной машине сгенерировать SSH-ключ:

```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

Скопировать публичный ключ на сервер:

```bash
ssh-copy-id -i ~/.ssh/github_actions.pub user@server-ip
```

Содержимое `~/.ssh/github_actions` (приватный ключ) добавить в GitHub Secret `SSH_KEY`.

### 4. Клонировать репозиторий на сервере

```bash
git clone <url-репозитория> ~/coursework_finale
cd ~/coursework_finale
```

### 5. Создать .env на сервере

```bash
cp .env.sample .env
nano .env  # заполнить реальными значениями
```

Важно для продакшна:

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,server-ip
SECRET_KEY=длинная-случайная-строка
```

### 6. Первый запуск на сервере

```bash
docker compose up -d --build
```

После этого GitHub Actions будет автоматически деплоить при каждом пуше в нужную ветку.

---

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `SECRET_KEY` | Django секретный ключ | `django-insecure-...` |
| `DEBUG` | Режим отладки | `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Имя базы данных | `coursework_finale` |
| `POSTGRES_USER` | Пользователь БД | `postgres` |
| `POSTGRES_PASSWORD` | Пароль БД | — |
| `HOST` | Хост БД | `db` |
| `PORT` | Порт БД | `5432` |
| `CELERY_BROKER_URL` | URL брокера Celery | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Backend результатов | `redis://redis:6379/0` |
| `STRIPE_SECRET_KEY` | Ключ Stripe API | `sk_live_...` |
| `EMAIL_HOST` | SMTP сервер | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | Email отправителя | — |
| `EMAIL_HOST_PASSWORD` | Пароль / App Password | — |
