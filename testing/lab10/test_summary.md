# Итоговый отчёт о тестировании — ЛР №10

## Версия и дата

- **Версия**: коммит `feature/lab10` (ЛР №10)
- **Дата тестирования**: 2026-11-14
- **Среда**: локально (pytest, in-memory SQLite), удалённо — Render (ручные тесты ЛР №9)

## Результаты ручного тестирования (ЛР №9)

- Всего тест-кейсов: **22**
- Выполнено: **22**
- PASS: **22**
- FAIL: **0**
- BLOCKED: **0**
- Показатель успешности: **22 / (22 + 0) × 100% = 100%**

## Дефекты

- Найдено: **0**
- Исправлено: **0**
- Неисправленных: **0**

## Автоматические тесты (ЛР №10)

- Всего автотестов: **16**
- PASS: **16**
- FAIL: **0**
- Команда запуска: `python -m pytest testing/lab10/test_api.py -v`
- Покрытие: **73%** (`--cov=src`)

### Категории

| Категория | Кол-во | Тесты |
|---|---|---|
| Бизнес-логика | 4 | test_service_list_requests, test_service_create_request, test_service_search_requests, test_service_change_status |
| API | 4 | test_api_list_requests, test_api_get_request_ok, test_api_create_request, test_api_delete_request |
| Валидация/негативные | 4 | test_api_create_empty_title, test_api_create_invalid_category, test_api_get_request_not_found, test_api_assign_non_executor |
| Регрессионные | 4 | test_regression_health, test_regression_search_after_status_change, test_regression_filters_combined, test_regression_integration_create_read |

### Покрытие по файлам

| Файл | Stmts | Miss | Cover |
|---|---|---|---|
| src/api.py | 69 | 18 | 74% |
| src/db.py | 12 | 4 | 67% |
| src/main.py | 7 | 0 | 100% |
| src/models.py | 42 | 0 | 100% |
| src/schemas.py | 27 | 0 | 100% |
| src/services.py | 112 | 51 | 54% |
| **TOTAL** | **269** | **73** | **73%** |

### Что не покрыто

- `src/services.py` (54%) — ветки обработки ошибок БД, `update_request`, `add_comment`, `delete_request` (частично).
- `src/db.py` (67%) — подключение к реальной БД (в тестах подменяется фикстурой `get_db`).
- `src/api.py` (74%) — PATCH-сценарии, часть обработчиков ошибок.

## Известные ограничения

- На Python 3.15 pytest выдаёт 83 `DeprecationWarning` от starlette/fastapi и `datetime.utcnow()`. На работу тестов не влияют, но в будущем потребуют обновления зависимостей.
- Тесты используют in-memory SQLite; на проде — файловая SQLite в контейнере Render.
- Нет тестов на авторизацию/аутентификацию (в проекте не реализованы).
- Нет нагрузочных тестов.

## Вывод о готовности

Продукт **готов к итоговой демонстрации**:
- 22/22 ручных тест-кейса PASS (100%)
- 16/16 автотестов PASS (100%)
- 0 дефектов
- Покрытие 73% (достаточно для учебного проекта)
- Приложение работает на Render (`/health`, `/docs`, `/api/requests`)
- README содержит инструкцию локального запуска и деплоя
