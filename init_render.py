import os
import sqlite3

DB_PATH = "request_system.db"

if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open("schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    with open("seed.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    print("БД создана и наполнена")
else:
    print("БД уже существует")