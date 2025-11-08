# Incident API Service

Этот сервис — маленькое REST API для учёта инцидентов с сохранением в SQLite.

## Требования

- Python 3.7+
- fastapi
- uvicorn
- pydantic

## Установка

1. Клонируйте репозиторий или сохраните файлы.
2. Установите зависимости:

pip install -r requirements.txt

## Запуск

Из корня проекта выполните:

uvicorn main:app --reload

После запуска сервис будет доступен по адресу http://127.0.0.1:8000

## Эндпоинты

### Создать инцидент

`POST /incidents`

Тело запроса JSON с полями:
- `description`: строка, описание инцидента
- `status`: строка, статус (open, in_progress, resolved, closed)
- `source`: строка, источник сообщения

Пример:

curl -X POST http://127.0.0.1:8000/incidents -H "Content-Type: application/json" -d '{"description":"Самокат не в сети","status":"open","source":"operator"}'

### Получить список инцидентов

`GET /incidents`

Поддерживается необязательный параметр `status` для фильтрации по статусу.

Пример:

curl http://127.0.0.1:8000/incidents?status=open

### Обновить статус инцидента

`PUT /incidents/{id}`

Тело запроса JSON с полем:
- `new_status`: новый статус

Пример:

curl -X PUT http://127.0.0.1:8000/incidents/<id> -H "Content-Type: application/json" -d '{"new_status":"resolved"}'

