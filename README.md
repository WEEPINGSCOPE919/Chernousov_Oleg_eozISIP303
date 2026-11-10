# Система учёта заявок

Учебный проект по дисциплине «Технологии разработки программного обеспечения».
Система позволяет создавать, просматривать, редактировать заявки, назначать исполнителей,
менять статус, добавлять комментарии, искать и фильтровать.

## Стек

- Python 3.12
- FastAPI 0.115
- SQLAlchemy 2.1
- Pydantic 2.14
- SQLite
- Docker

## Структура проекта

```
.
├── src/
│   ├── main.py
│   ├── api.py
│   ├── schemas.py
│   ├── services.py
│   ├── models.py
│   └── db.py
├── docs/
│   ├── db/
│   └── ai_log.md
├── Dockerfile
├── init_render.py
├── requirements.txt
└── README.md
```

## Локальный запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/WEEPINGSCOPE919/Chernousov_Oleg_eozISIP303.git
cd Chernousov_Oleg_eozISIP303
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

### 3. Создать БД и наполнить тестовыми данными

```bash
cd docs/db
python init_db.py
cd ../..
mv docs/db/request_system.db ./request_system.db
```

### 4. Запустить приложение

```bash
uvicorn src.main:app --reload --port 8000
```

Открыть в браузере:
- Swagger UI: http://127.0.0.1:8000/docs
- Health-check: http://127.0.0.1:8000/health

## Запуск в Docker

```bash
docker build -t request-system .
docker run -p 8000:8000 -e PORT=8000 request-system
```

Приложение будет доступно на http://127.0.0.1:8000/docs.

## Деплой на Render

1. Зарегистрироваться на https://render.com (через GitHub).
2. New + → Web Service → подключить репозиторий Chernousov_Oleg_eozISIP303.
3. Настройки:
   - Language: Docker
   - Branch: main
   - Region: Oregon
   - Root Directory: пусто
   - Dockerfile Path: .
4. Create Web Service. Render соберёт образ и запустит контейнер.
5. После статуса Live приложение доступно по адресу:
   https://chernousov-oleg-eozisip303.onrender.com

Примечание: на бесплатном тарифе Render сервис засыпает через 15 минут простоя.
Первый запрос после сна грузится ~1 минуту. Это нормально.

## API

Базовый URL (удалённо): https://chernousov-oleg-eozisip303.onrender.com
Базовый URL (локально): http://127.0.0.1:8000

| Метод | Путь | Назначение | Коды |
|---|---|---|---|
| GET | /health | Проверка доступности | 200 |
| GET | /api/requests | Список заявок (фильтры: status_id, category_id, executor_id, search) | 200 |
| GET | /api/requests/{id} | Получить заявку | 200, 404 |
| POST | /api/requests | Создать заявку | 201, 422 |
| PATCH | /api/requests/{id} | Изменить заявку | 200, 404, 422 |
| DELETE | /api/requests/{id} | Удалить заявку | 204, 404 |
| POST | /api/requests/{id}/status | Сменить статус | 200, 404, 422 |
| POST | /api/requests/{id}/assign | Назначить исполнителя | 200, 404, 422 |
| POST | /api/requests/{id}/comments | Добавить комментарий | 201, 404, 422 |
| GET | /api/users | Список пользователей | 200 |
| GET | /api/categories | Справочник категорий | 200 |
| GET | /api/statuses | Справочник статусов | 200 |

### Пример запроса (curl)

```bash
curl -X POST https://chernousov-oleg-eozisip303.onrender.com/api/requests \
  -H "Content-Type: application/json" \
  -d '{"title":"Тест","description":"Проверка","category_id":1,"status_id":1,"applicant_id":4}'
```

### Пример ответа

```json
{
  "id": 6,
  "title": "Тест",
  "description": "Проверка",
  "created_at": "2026-11-10T13:20:00",
  "category_id": 1,
  "status_id": 1,
  "applicant_id": 4,
  "executor_id": null,
  "category": {"id": 1, "name": "Оборудование"},
  "status": {"id": 1, "name": "Новая"},
  "applicant": {"id": 4, "full_name": "Заявитель Петров", "email": "petrov@example.com", "role": "applicant"},
  "executor": null,
  "comments": []
}
```

## Тестовые данные

В БД при инициализации загружаются:
- 5 пользователей (admin, operator, 2 executor, applicant)
- 4 категории (Оборудование, ПО, Доступы, Прочее)
- 4 статуса (Новая, В работе, Выполнена, Закрыта)
- 5 заявок
- 4 комментария

Полный список — в docs/db/seed.sql.