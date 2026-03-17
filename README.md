# Foodgram — Продуктовый помощник

[![CI/CD](https://github.com/Andrey75rr/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Andrey75rr/foodgram/actions/workflows/main.yml)

Foodgram — сервис для публикации рецептов. Пользователи могут создавать рецепты, добавлять их в избранное и список покупок, подписываться на других авторов, а также скачивать список покупок в виде текстового файла.

## Технологии

- Python 3.12
- Django 6.0
- Django REST Framework 3.16
- Djoser
- PostgreSQL
- Nginx
- Docker / Docker Compose
- GitHub Actions (CI/CD)

## Запуск проекта локально

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Andrey75rr/foodgram.git
cd foodgram
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настроить переменные окружения

Создать файл `backend/.env` (для локальной разработки):

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_DB=foodgram_db
DB_HOST=db
DB_PORT=5432
```

### 4. Выполнить миграции и запустить сервер

```bash
python manage.py migrate
python manage.py load_ingredients
python manage.py runserver
```

## Запуск в Docker

```bash
cd infra
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py load_ingredients
```

## Деплой на сервер

Деплой выполняется автоматически через GitHub Actions при пуше в ветку `main`.

Для настройки деплоя добавить в GitHub Secrets:

| Secret | Описание |
|--------|----------|
| `DOCKER_USERNAME` | Логин Docker Hub |
| `DOCKER_PASSWORD` | Пароль Docker Hub |
| `HOST` | IP адрес сервера |
| `USER` | Пользователь сервера |
| `SSH_KEY` | Приватный SSH ключ |
| `SSH_PASSPHRASE` | Пароль SSH ключа |
| `TELEGRAM_TO` | ID Telegram чата |
| `TELEGRAM_TOKEN` | Токен Telegram бота |

На сервере создать файл `~/foodgram/.env` с переменными окружения (аналогично локальному, но с `DEBUG=False` и реальными данными).

## Примеры запросов API

### Регистрация пользователя

```http
POST /api/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "password": "password123"
}
```

### Получение токена

```http
POST /api/auth/token/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Создание рецепта

```http
POST /api/recipes/
Authorization: Token <your_token>
Content-Type: application/json

{
  "ingredients": [{"id": 1, "amount": 100}],
  "tags": [1, 2],
  "image": "data:image/png;base64,...",
  "name": "Название рецепта",
  "text": "Описание рецепта",
  "cooking_time": 30
}
```

### Добавить рецепт в избранное

```http
POST /api/recipes/{id}/favorite/
Authorization: Token <your_token>
```

### Скачать список покупок

```http
GET /api/recipes/download_shopping_cart/
Authorization: Token <your_token>
```

## Документация API

После запуска проекта документация доступна по адресу:

```
http://localhost/api/docs/
```

## Автор

**Андрей Тихончук**
- GitHub: [Andrey75rr](https://github.com/Andrey75rr)
- сайт доступен по адресу(http://158.160.15.55/)
