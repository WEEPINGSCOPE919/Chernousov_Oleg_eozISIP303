FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY docs/db/schema.sql ./schema.sql
COPY docs/db/seed.sql ./seed.sql
COPY init_render.py .

EXPOSE 8000

CMD ["sh", "-c", "python init_render.py && uvicorn src.main:app --host 0.0.0.0 --port $PORT"]