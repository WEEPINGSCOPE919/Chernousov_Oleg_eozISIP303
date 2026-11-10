from src.db import SessionLocal
from src.models import User, Request, Category, Status

db = SessionLocal()
print("Users:", db.query(User).count())
print("Requests:", db.query(Request).count())
print("Categories:", db.query(Category).count())
print("Statuses:", db.query(Status).count())
db.close()