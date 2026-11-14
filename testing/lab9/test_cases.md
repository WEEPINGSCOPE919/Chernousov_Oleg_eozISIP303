# Тест-кейсы — ЛР №9

**Версия**: коммит `0eb9fbd`, дата 2026-11-14
**Среда**: https://chernousov-oleg-eozisip303.onrender.com
**Результат прогона**: 22 PASS, 0 FAIL, 0 BLOCKED

| ID | Категория | Цель | Входные данные | Ожидаемый результат | Фактический результат | Статус | Доказательство |
|---|---|---|---|---|---|---|---|
| TC-01 | Позитивный | Создание заявки | `{"title":"Тест","description":"Описание","category_id":1,"status_id":1,"applicant_id":4}` | 201, id | 201, id=6 | PASS | TC-01.png |
| TC-02 | Позитивный | Список заявок | — | 200, массив | 200 | PASS | curl output |
| TC-03 | Позитивный | Заявка id=1 | request_id=1 | 200, «Не работает принтер» | 200 | PASS | curl output |
| TC-04 | Позитивный | Смена статуса на 2 | `{"status_id":2}` | 200, status_id=2 | 200 | PASS | curl output |
| TC-05 | Позитивный | Назначение исполнителя id=3 | `{"user_id":3}` | 200, executor_id=3 | 200 | PASS | curl output |
| TC-06 | Позитивный | Комментарий | `{"user_id":4,"text":"Комментарий из теста"}` | 201 | 201 | PASS | curl output |
| TC-07 | Позитивный | Поиск VPN | search=VPN | 200, 1 заявка | 200 | PASS | curl output |
| TC-08 | Позитивный | Фильтр статус=2 | status_id=2 | 200, заявки со статусом 2 | 200 | PASS | curl output |
| TC-09 | Негативный | Пустой title | `{"title":"","category_id":1,"status_id":1,"applicant_id":4}` | 422 | 422 | PASS | TC-09.png |
| TC-10 | Негативный | Категория 999 | `{"title":"Тест","category_id":999,"status_id":1,"applicant_id":4}` | 422 | 422 | PASS | curl output |
| TC-11 | Негативный | Заявка 99999 | request_id=99999 | 404 | 404 | PASS | TC-11.png |
| TC-12 | Негативный | Назначить не-executor | `{"user_id":4}` | 422 | 422 | PASS | curl output |
| TC-13 | Негативный | Статус 999 | `{"status_id":999}` | 422 | 422 | PASS | curl output |
| TC-14 | Граничный | Title 1 символ | `{"title":"A",...}` | 201 | 201 | PASS | curl output |
| TC-15 | Граничный | Title 200 символов | `{"title":"<200 A>",...}` | 201 | 201 | PASS | curl output |
| TC-16 | Граничный | Title 201 символ | `{"title":"<201 A>",...}` | 422 | 422 | PASS | curl output |
| TC-17 | Граничный | Спецсимволы | `{"title":"Тест <>&\"'",...}` | 201 | 201 | PASS | curl output |
| TC-18 | Интеграционный | Создать → прочитать | POST + GET | 201, потом 200 | 201, потом 200 | PASS | TC-18.png |
| TC-19 | Интеграционный | Статус → прочитать | POST status + GET | 200, 200 | 200, 200 | PASS | curl output |
| TC-20 | API | DELETE заявки | DELETE id=6 | 204 | 204 | PASS | curl output |
| TC-21 | API | DELETE несуществующей | DELETE 99999 | 404 | 404 | PASS | curl output |
| TC-22 | API | Health | GET /health | 200, `{"status":"ok"}` | 200 | PASS | TC-22.png |

## Сводка

| Категория | Кол-во | PASS | FAIL |
|---|---|---|---|
| Позитивные | 8 | 8 | 0 |
| Негативные | 5 | 5 | 0 |
| Граничные | 4 | 4 | 0 |
| Интеграционные | 2 | 2 | 0 |
| API | 3 | 3 | 0 |
| **Итого** | **22** | **22** | **0** |

## Дефекты

Дефектов не обнаружено. Все 22 тест-кейса прошли с ожидаемыми результатами.
