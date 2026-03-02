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

### 1. Клонирование репозитория
```bash
git clone <url-репозитория>
cd Viewsets@Generics
```

### 2. Создание виртуального окружения
```bash
python -m venv .venv
.venv\Scripts\activate  # для Windows
source .venv/bin/activate  # для Linux/Mac
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
SECRET_KEY=your-secret-key
NAME=database_name
DB_USER=database_user
PASSWORD=database_password
HOST=localhost
PORT=5432
```

### 5. Применение миграций
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание группы модераторов
```bash
python manage.py create_groups
```

### 7. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 8. Запуск сервера
```bash
python manage.py runserver
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

## Лицензия

Учебный проект

## Автор

Создано в рамках выполнения домашнего задания №31
