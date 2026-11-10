from src.db import SessionLocal
from src.services import (
    list_requests, get_request, create_request, change_status,
    assign_executor, add_comment, delete_request, list_statuses,
    ValidationError, NotFoundError,
)

db = SessionLocal()

print("=== Все заявки ===")
for r in list_requests(db):
    print(f"#{r.id} {r.title} | status={r.status_id} | executor={r.executor_id}")

print("\n=== Фильтр по статусу 2 ===")
for r in list_requests(db, status_id=2):
    print(f"#{r.id} {r.title}")

print("\n=== Поиск 'VPN' ===")
for r in list_requests(db, search="VPN"):
    print(f"#{r.id} {r.title}")

print("\n=== Создание новой заявки ===")
new = create_request(db, title="Тестовая заявка", description="Проверка сервиса",
                     category_id=1, status_id=1, applicant_id=4)
print(f"Создана #{new.id} {new.title}")

print("\n=== Смена статуса на 2 ===")
updated = change_status(db, new.id, 2)
print(f"Статус теперь {updated.status_id}")

print("\n=== Назначение исполнителя id=3 ===")
assigned = assign_executor(db, new.id, 3)
print(f"Исполнитель {assigned.executor_id}")

print("\n=== Комментарий ===")
c = add_comment(db, new.id, 4, "Комментарий из проверки")
print(f"Комментарий #{c.id}")

print("\n=== Ошибка: несуществующая заявка ===")
try:
    get_request(db, 99999)
except NotFoundError as e:
    print(f"OK, поймали: {e}")

print("\n=== Ошибка: пустой title ===")
try:
    create_request(db, title="  ", description=None, category_id=1,
                   status_id=1, applicant_id=4)
except ValidationError as e:
    print(f"OK, поймали: {e}")

print("\n=== Удаление тестовой заявки ===")
delete_request(db, new.id)
print(f"Удалена #{new.id}")

db.close()