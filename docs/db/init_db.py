import sqlite3

conn = sqlite3.connect('request_system.db')
cursor = conn.cursor()

with open('schema.sql', 'r', encoding='utf-8') as f:
    cursor.executescript(f.read())

with open('seed.sql', 'r', encoding='utf-8') as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()
print("База создана: request_system.db")