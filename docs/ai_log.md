
# AI-журнал (ЛР №6–8)



\## ЛР №6. Разработка функционала



\### AI-взаимодействие №1: проектирование сервисного слоя



\- \*\*Дата/этап\*\*: 2026-11-06, до написания `src/services.py`.

\- \*\*Задача\*\*: спроектировать функции сервисного слоя для CRUD заявок, поиска, фильтрации, смены статуса, назначения исполнителя, комментариев.

\- \*\*Модель\*\*:DeepSeek V3.

\- \*\*Промпт \*\*: Ниже представлен production-ready Dockerfile с учётом вашей структуры проекта и требований к развёртыванию на Render (free). Ключевой момент: поскольку файловая система Render эфемерна, SQLite-БД будет создаваться заново при каждом перезапуске/деплое — это осознанный компромисс для бесплатного тарифа.



dockerfile

\# ============================================================

\# Stage 1: Builder — установка зависимостей

\# ============================================================

FROM python:3.12-slim AS builder



WORKDIR /build



\# Системные зависимости для сборки (если нужны)

RUN apt-get update \&\& apt-get install -y --no-install-recommends \\

&#x20;   gcc \\

&#x20;   \&\& rm -rf /var/lib/apt/lists/\*



\# Кеширование зависимостей: копируем только requirements

COPY requirements.txt .



\# Устанавливаем в отдельную директорию для переноса в финальный образ

RUN pip install --no-cache-dir --user -r requirements.txt



\# ============================================================

\# Stage 2: Runtime — минимальный образ

\# ============================================================

FROM python:3.12-slim



\# Метаданные

LABEL maintainer="app" \\

&#x20;     description="FastAPI + SQLAlchemy + SQLite on Render"



\# Переменные окружения Python

ENV PYTHONDONTWRITEBYTECODE=1 \\

&#x20;   PYTHONUNBUFFERED=1 \\

&#x20;   PYTHONPATH=/app \\

&#x20;   PORT=8000



WORKDIR /app



\# Устанавливаем sqlite3 CLI для инициализации БД и curl для health-check

RUN apt-get update \&\& apt-get install -y --no-install-recommends \\

&#x20;   sqlite3 \\

&#x20;   curl \\

&#x20;   \&\& rm -rf /var/lib/apt/lists/\* \\

&#x20;   \&\& useradd --create-home --shell /bin/bash appuser



\# Копируем установленные зависимости из builder

COPY --from=builder /root/.local /home/appuser/.local



\# Копируем исходный код и SQL-файлы

COPY --chown=appuser:appuser src/ ./src/

COPY --chown=appuser:appuser schema.sql seed.sql ./



\# Скрипт инициализации БД (создаётся как отдельный файл)

COPY --chown=appuser:appuser init\_db.sh ./

RUN chmod +x init\_db.sh



\# Переключаемся на non-root пользователя

USER appuser



\# Добавляем локальные bin в PATH

ENV PATH="/home/appuser/.local/bin:${PATH}"



\# Health-check (FastAPI должен иметь эндпоинт /health)

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\

&#x20;   CMD curl -fsS http://localhost:${PORT}/health || exit 1



\# Открываем порт (информативно, Render использует $PORT)

EXPOSE ${PORT}



\# Инициализация БД и запуск приложения

\# Используем exec-форму для корректного graceful shutdown

ENTRYPOINT \["./init\_db.sh"]

CMD \["sh", "-c", "exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]

Файл init\_db.sh (положите в корень проекта):



bash

\#!/bin/sh

set -e



DB\_FILE="./app.db"



\# Создаём БД, только если файла нет

if \[ ! -f "$DB\_FILE" ]; then

&#x20;   echo "Creating SQLite database from schema.sql and seed.sql..."

&#x20;   sqlite3 "$DB\_FILE" < schema.sql

&#x20;   sqlite3 "$DB\_FILE" < seed.sql

&#x20;   echo "Database initialized."

else

&#x20;   echo "Database already exists, skipping initialization."

fi



\# Передаём управление CMD

exec "$@"

Пояснения по ключевым решениям

Multi-stage build: зависимости устанавливаются в builder, затем копируются в чистый runtime-образ. Это уменьшает размер финального образа и убирает компиляторы из production.



Кеширование: requirements.txt копируется до исходного кода — Docker переиспользует слой с pip install, пока зависимости не изменятся .



Non-root user: создаётся appuser, все файлы копируются с --chown. Контейнер не запускается от root.



Health-check: используется curl к эндпоинту /health. Убедитесь, что в src/main.py или src/api.py есть такой маршрут (например, @app.get("/health"), возвращающий {"status": "ok"}). Render использует healthCheckPath в конфигурации сервиса, но Docker HEALTHCHECK полезен для локальной проверки и оркестраторов .



Переменная $PORT: Render автоматически задаёт PORT (обычно 10000). В CMD используется sh -c для подстановки переменной. По умолчанию в ENV задано 8000 для локального запуска.



Важное предупреждение о SQLite на Render Free

Файловая система Render на бесплатном тарифе эфемерна: при каждом деплое, перезапуске или пробуждении из «сна» контейнер начинается с чистого образа. Ваш init\_db.sh создаст БД заново из schema.sql и seed.sql. Все данные, записанные пользователями, будут потеряны.



Если требуется сохранение данных, единственный вариант на Render — платный план с постоянным диском (Persistent Disk), монтируемым в /data . В этом случае нужно изменить DB\_FILE на /data/app.db и добавить диск через дашборд Render.



Необходимые файлы в репозитории

Убедитесь, что в корне проекта есть:



requirements.txt (fastapi, uvicorn\[standard], sqlalchemy, и т.д.)



schema.sql (DDL)



seed.sql (INSERT-ы)



src/ с модулями main.py, api.py, services.py, models.py, db.py



init\_db.sh (из примера выше)



Если в db.py путь к БД задаётся через переменную окружения (например, DATABASE\_URL=sqlite:///./app.db), убедитесь, что он совпадает с путём в init\_db.sh«Помоги написать сервисный слой для системы учёта заявок на Python».

\- \*\*ПромптРазбираю ваш Dockerfile по всем восьми пунктам. Файл короткий, и в нём сконцентрировано несколько типичных проблем, которые на Render free могут привести к падениям деплоя или уязвимостям.



Исходник для удобства:



dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

COPY docs/db/schema.sql ./schema.sql

COPY docs/db/seed.sql ./seed.sql

COPY init\_render.py .

EXPOSE 8000

CMD \["sh", "-c", "python init\_render.py \&\& uvicorn src.main:app --host 0.0.0.0 --port $PORT"]

1\. Безопасность

Что не так:



Контейнер запускается от root (в python:3.12-slim по умолчанию пользователь root). Любой RCE в приложении = root внутри контейнера, а при неудачной конфигурации — потенциальный выход на хост.



Нет фиксации версии базового образа — python:3.12-slim это плавающий тег, при каждом билде может подтянуться другой образ с другими CVE или сломанными зависимостями.



Нет --no-install-recommends и очистки apt-кеша (правда, apt вы не используете — это плюс, но если добавите системные пакеты, нужно не забыть).



Нет PYTHONDONTWRITEBYTECODE / PYTHONUNBUFFERED — не критично для безопасности, но unbuffered важен для логов (см. п. 8).



Как исправить:



dockerfile

FROM python:3.12.7-slim-bookworm AS base   # фиксируем версию



ENV PYTHONDONTWRITEBYTECODE=1 \\

&#x20;   PYTHONUNBUFFERED=1 \\

&#x20;   PIP\_NO\_CACHE\_DIR=1 \\

&#x20;   PIP\_DISABLE\_PIP\_VERSION\_CHECK=1



\# ... установка ...



RUN useradd --create-home --shell /bin/bash appuser

USER appuser

Дополнительно: регулярно пересобирайте образ (Render это делает при деплое) и следите за обновлениями python:3.12.x-slim-bookworm.



2\. Размер образа

Что не так:



Single-stage — в финальном образе остаются pip, кеш pip (частично погашен --no-cache-dir), но главное — нет разделения builder/runtime. Для чистого Python без C-расширений выгода от multi-stage небольшая, но если в requirements.txt есть, например, psycopg2, cryptography, pandas — в образе останутся gcc, libpq-dev, build-essential.



pip install без --user устанавливает пакеты в системный site-packages — при multi-stage их нельзя просто скопировать.



Нет .dockerignore (см. п. 3) — в контекст сборки могут попасть .git, .env, \_\_pycache\_\_, \*.db, тесты.



Как исправить: multi-stage с --user или --prefix:



dockerfile

FROM python:3.12.7-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt



FROM python:3.12.7-slim-bookworm AS runtime

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

ENV PATH="/home/appuser/.local/bin:${PATH}"

\# ...

И обязательно .dockerignore:



text

.git

.gitignore

.env

\*.db

\_\_pycache\_\_/

\*.pyc

.pytest\_cache/

.venv/

docs/

README.md

Dockerfile

.dockerignore

Обратите внимание: вы копируете docs/db/schema.sql и docs/db/seed.sql — если в docs/ есть что-то ещё (скриншоты, PDF), оно не попадёт в образ, потому что вы копируете точечно. Это правильно. Но .dockerignore всё равно нужен для контекста сборки.



3\. Кеширование слоёв

Что не так:



Порядок в целом правильный: requirements.txt → pip install → код. Это хорошо, слой с зависимостями переиспользуется, пока не изменится requirements.txt.



Но есть нюанс: COPY src ./src идёт до копирования SQL-файлов и init\_render.py. Если меняется только init\_render.py или schema.sql, слой COPY src всё равно инвалидируется? Нет — COPY src инвалидируется только при изменении файлов в src/. Это нормально. Но если вы часто правите init\_render.py — он в конце, это правильно.



Проблема: нет --mount=type=cache для pip (BuildKit). На Render BuildKit доступен, это ускорит пересборки.



Как исправить (опционально, BuildKit):



dockerfile

\# syntax=docker/dockerfile:1.7

RUN --mount=type=cache,target=/root/.cache/pip \\

&#x20;   pip install -r requirements.txt

Если BuildKit на Render не включён — оставьте --no-cache-dir, это безопасный fallback.



4\. Порты

Что не так:



EXPOSE 8000 — это только документация, Render её игнорирует. Render подставляет свою переменную $PORT (обычно 10000). Ваш CMD использует $PORT — это правильно.



Но EXPOSE 8000 вводит в заблуждение: локально порт будет 8000 (если $PORT не задан), на Render — 10000. Лучше EXPOSE ${PORT} не работает в EXPOSE (переменные там не раскрываются), поэтому либо убрать EXPOSE, либо оставить как документирующий комментарий.



$PORT не имеет значения по умолчанию. Если переменная не задана (локальный docker run), uvicorn --port $PORT получит пустую строку и упадёт. Нужен fallback.



Как исправить:



dockerfile

ENV PORT=8000

\# EXPOSE ${PORT}  # не раскрывается, лучше закомментировать или убрать



CMD \["sh", "-c", "python init\_render.py \&\& exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

Или в init\_render.py/main.py читать os.getenv("PORT", "8000").



5\. Права пользователя

Что не так:



Контейнер работает от root. Это главная проблема безопасности.



WORKDIR /app создаётся от root, файлы копируются с root:root. Даже если добавить USER appuser после COPY, приложение не сможет писать в /app (например, SQLite-файл app.db), если не сделать chown.



init\_render.py создаёт SQLite-БД — куда? Если в /app/app.db, а /app принадлежит root, запись упадёт с Permission denied.



Как исправить:



dockerfile

RUN useradd --create-home --shell /bin/bash appuser



WORKDIR /app

COPY --chown=appuser:appuser requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt   # от root — ок, системный site-packages



COPY --chown=appuser:appuser src ./src

COPY --chown=appuser:appuser docs/db/schema.sql ./schema.sql

COPY --chown=appuser:appuser docs/db/seed.sql ./seed.sql

COPY --chown=appuser:appuser init\_render.py .



USER appuser

Либо, если хотите писать БД в отдельную директорию:



dockerfile

RUN mkdir -p /app/data \&\& chown appuser:appuser /app/data

ENV DATABASE\_PATH=/app/data/app.db

6\. Секреты

Что не так:



В самом Dockerfile секретов нет — это хорошо.



Но есть риск: если init\_render.py или приложение читает .env, а .dockerignore отсутствует — .env может попасть в образ через COPY. У вас COPY точечный, так что .env не скопируется, но .dockerignore всё равно нужен как страховка.



DATABASE\_URL и другие секреты должны приходить только через переменные окружения Render (Environment Variables в дашборде), не через ENV/ARG в Dockerfile.



Как исправить: ничего не менять в Dockerfile, но:



добавить .dockerignore с .env, \*.pem, \*.key, secrets/;



убедиться, что в init\_render.py и db.py нет хардкода паролей/токенов;



использовать ENV только для нечувствительных значений (PORT, PYTHONUNBUFFERED).



7\. Health-check

Что не так:



HEALTHCHECK отсутствует. Docker не знает, жив ли контейнер. На Render это частично компенсируется healthCheckPath в настройках сервиса, но:



без HEALTHCHECK локальный docker run и оркестраторы (k8s, ECS) не перезапустят зависший контейнер;



Render free всё равно полагается на свой health-check, но лучше дублировать.



В python:3.12-slim нет curl по умолчанию. Если добавите HEALTHCHECK CMD curl ... — образ упадёт при старте. Нужно либо ставить curl, либо использовать python -c / wget (в slim есть wget? нет, тоже нет). Значит — python -c или установка curl.



Как исправить (без установки curl):



dockerfile

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \\

&#x20;   CMD python -c "import urllib.request,sys,os; \\

&#x20;       sys.exit(0) if urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\\"PORT\\",\\"8000\\")}/health', timeout=3).status==200 else sys.exit(1)"

Или установить curl (добавит \~10 МБ, но проще):



dockerfile

RUN apt-get update \&\& apt-get install -y --no-install-recommends curl \\

&#x20;   \&\& rm -rf /var/lib/apt/lists/\*

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \\

&#x20;   CMD curl -fsS "http://127.0.0.1:${PORT:-8000}/health" || exit 1

Важно: убедитесь, что эндпоинт /health реально существует в src/main.py/src/api.py и не требует авторизации.



8\. Обработка переменных окружения

Что не так:



$PORT без default. Уже разобрано в п. 4 — при локальном запуске без -e PORT uvicorn упадёт.



sh -c "python init\_render.py \&\& uvicorn ..." — две проблемы:



Нет exec перед uvicorn. sh остаётся PID 1 и не пробрасывает SIGTERM дочернему процессу корректно. На Render при остановке контейнера uvicorn не получит graceful shutdown → обрыв соединений, незакрытые SQLite-транзакции, потенциальная порча БД.

Если init\_render.py завершится с ненулевым кодом — контейнер упадёт (это ок), но без логов причины.

PYTHONUNBUFFERED не задан — логи uvicorn/print буферизуются, на Render логи могут появляться с задержкой или теряться при падении.



PYTHONPATH — если src.main:app не находится, uvicorn упадёт. WORKDIR /app обычно достаточно (Python добавляет cwd в sys.path), но если в src/ есть относительные импорты вида from src.services import ... — нужен PYTHONPATH=/app.



Как исправить:



dockerfile

ENV PYTHONUNBUFFERED=1 \\

&#x20;   PYTHONDONTWRITEBYTECODE=1 \\

&#x20;   PYTHONPATH=/app \\

&#x20;   PORT=8000



\# ...



CMD \["sh", "-c", "python init\_render.py \&\& exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

Альтернатива — entrypoint-скрипт entrypoint.sh:



sh

\#!/bin/sh

set -e

python init\_render.py

exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}"

и ENTRYPOINT \["/app/entrypoint.sh"]. Это чище, чем sh -c в CMD, и корректно обрабатывает сигналы.



Сводная таблица

Пункт	Серьёзность	Проблема	Исправление

Безопасность	🔴 Высокая	root-пользователь	useradd + USER appuser + --chown

Безопасность	🟡 Средняя	плавающий тег 3.12-slim	python:3.12.7-slim-bookworm

Размер	🟡 Средняя	single-stage, нет .dockerignore	multi-stage + .dockerignore

Кеширование	🟢 Низкая	нет BuildKit cache mount	--mount=type=cache (опционально)

Порты	🔴 Высокая	$PORT без default → падение локально	${PORT:-8000}

Порты	🟢 Низкая	EXPOSE 8000 вводит в заблуждение	убрать/комментировать

Права	🔴 Высокая	/app принадлежит root, SQLite не пишется	--chown=appuser:appuser на COPY

Секреты	🟢 Низкая	нет .dockerignore как страховки	добавить .dockerignore

Health-check	🟡 Средняя	отсутствует	HEALTHCHECK через python -c или curl

Env	🔴 Высокая	нет exec, нет PYTHONUNBUFFERED, нет PYTHONPATH	exec uvicorn, ENV-блок

Итоговый исправленный Dockerfile

dockerfile

\# syntax=docker/dockerfile:1.7

FROM python:3.12.7-slim-bookworm AS builder



WORKDIR /build

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \\

&#x20;   pip install --user -r requirements.txt





FROM python:3.12.7-slim-bookworm AS runtime



ENV PYTHONUNBUFFERED=1 \\

&#x20;   PYTHONDONTWRITEBYTECODE=1 \\

&#x20;   PYTHONPATH=/app \\

&#x20;   PATH="/home/appuser/.local/bin:${PATH}" \\

&#x20;   PORT=8000



RUN useradd --create-home --shell /bin/bash appuser



WORKDIR /app



COPY --from=builder /root/.local /home/appuser/.local



COPY --chown=appuser:appuser src ./src

COPY --chown=appuser:appuser docs/db/schema.sql ./schema.sql

COPY --chown=appuser:appuser docs/db/seed.sql ./seed.sql

COPY --chown=appuser:appuser init\_render.py .

COPY --chown=appuser:appuser entrypoint.sh .

RUN chmod +x entrypoint.sh



USER appuser



HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \\

&#x20;   CMD python -c "import os,sys,urllib.request; \\

&#x20;       sys.exit(0) if urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\\"PORT\\",\\"8000\\")}/health', timeout=3).status==200 else sys.exit(1)"



ENTRYPOINT \["./entrypoint.sh"]

entrypoint.sh:



sh

\#!/bin/sh

set -e

python init\_render.py

exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}"

.dockerignore:



text

.git

.gitignore

.env

\*.db

\_\_pycache\_\_/

\*.pyc

.pytest\_cache/

.venv/

venv/

docs/

README.md

Dockerfile

.dockerignore

Отдельно напомню про эфемерность SQLite на Render free: init\_render.py будет пересоздавать БД при каждом холодном старте/деплое, и данные пользователей будут теряться. Если это не устраивает — нужен либо Persistent Disk (платный план), либо внешняя БД (Render PostgreSQL free tier).: «Контекст: учебный проект «Система учёта заявок». Стек: Python 3.15, FastAPI, SQLAlchemy 2.1, Pydantic 2.14, SQLite. Схема БД: Users(id, full\_name, email UNIQUE, role), Categories(id, name), Statuses(id, name), Requests(id, title, description, created\_at, category\_id, status\_id, applicant\_id, executor\_id), Comments(id, request\_id, user\_id, text, created\_at). Задача: спроектировать сервисный слой для CRUD, поиска, фильтрации, смены статуса, назначения исполнителя, комментариев. Бизнес-логика только в сервисе. Требования к ответу: сигнатуры функций, что валидирует, какие исключения кидает, без кода реализации».

\- \*\*Контекст\*\*: схема БД, стек, требование «бизнес-логика только в сервисе».

\- \*\*Результат\*\*: модель предложила список функций с сигнатурами, кастомные исключения `NotFoundError`, `ValidationError`, `ConflictError`, проверку роли `executor` при назначении исполнителя, поиск через `ilike` по title/description.

\- \*\*Проверка\*\*: написал `check\_services.py`, прогнал все функции (создание, фильтр, поиск, смена статуса, назначение, комментарий, удаление) + две ошибки (404, 422). Всё отработало.

\- \*\*Доработка\*\*: отклонил предложенное моделью поле `priority` (его нет в схеме); оставил удаление вместо архивации (в ТЗ архивация не выделена отдельно).

\- \*\*Почему такая модель/промпт\*\*: выбрал модель, которая хорошо знает FastAPI/SQLAlchemy. Промпт улучшил, добавив схему БД и ограничение «без кода» — иначе модель писала общий код, не привязанный к проекту.

\- \*\*Итог\*\*: в проект вошли функции `list\_requests`, `get\_request`, `create\_request`, `update\_request`, `change\_status`, `assign\_executor`, `add\_comment`, `delete\_request` и три кастомных исключения.



\## ЛР №7. REST API



\### AI-взаимодействие №2: контракт API и его критика



\- \*\*Дата/этап\*\*: 2026-11-10, перед написанием `src/api.py`.

\- \*\*Задача\*\*: получить API-контракт для сущности Request и критически проверить его.

\- \*\*Модель\*\*: \[укажи].

\- \*\*Промпт №1 (контракт)\*\*: «Предложи API-контракт для сущности Request: список эндпоинтов (CRUD + смена статуса + назначение исполнителя + комментарии), JSON-схемы запросов/ответов, HTTP-коды, правила валидации».

\- \*\*Промпт №2 (критика)\*\*: «Проверь критически мой контракт: корректны ли HTTP-коды, достаточно ли валидации, удобен ли формат ошибок для клиента, нет ли проблем безопасности (например, можно ли назначить исполнителем пользователя с другой ролью)».

\- \*\*Контекст\*\*: схема БД, требования ЛР №7 (7+ эндпоинтов, коды 200/201/204/400/404/422).

\- \*\*Результат\*\*: модель предложила 409 Conflict для UNIQUE email, 422 для несуществующих FK, единый формат ошибок `{"detail": "..."}`.

\- \*\*Проверка\*\*: прогнал 10 запросов в curl (GET list, GET by id, POST, PATCH, DELETE, assign, status, comments) + ошибочные (404, 422). Все коды совпали с ожидаемыми.

\- \*\*Доработка\*\*: принял идею 422 для несуществующих FK (реализовано в `\_validate\_request\_refs`); отклонил 400 — использую 422 везде для валидации.

\- \*\*Почему такая модель/промпт\*\*: модель хорошо знает REST-конвенции. Промпт с просьбой «проверь критически» дал более полезный ответ, чем просто «предложи контракт».

\- \*\*Итог\*\*: в проект вошли 12 эндпоинтов, единый формат ошибок, 422 для несуществующих FK, 404 для отсутствующих записей.



\## ЛР №8. Docker и деплой



\### AI-взаимодействие №3: генерация Dockerfile



\- \*\*Дата/этап\*\*: 2026-11-10, подготовка к деплою на Render.

\- \*\*Задача\*\*: получить черновик Dockerfile для FastAPI + SQLite с инициализацией БД.

\- \*\*Модель\*\*: DEEPSEEK v3.

\- \*\*Промпт\*\*: «Предложи Dockerfile для проекта на Python: Python 3.12, FastAPI + SQLAlchemy + SQLite, структура src/ с main.py, api.py, services.py, models.py, db.py, точка входа uvicorn src.main:app, порт из $PORT, при старте создать SQLite-БД из schema.sql и seed.sql, если её нет, деплой на Render (free), файловая система эфемерная. Дай production-ready Dockerfile: multi-stage или slim, non-root user, кеширование зависимостей, health-check».

\- \*\*Контекст\*\*: структура `src/`, `schema.sql`, `seed.sql`, требования Render (эфемерная ФС, `$PORT`).

\- \*\*Результат\*\*: модель предложила multi-stage build, non-root user, HEALTHCHECK, COPY только нужных файлов.

\- \*\*Проверка\*\*: собрал образ локально `docker build`, запустил `docker run`, проверил `/health` и `/api/requests`. На Render деплой прошёл, статус Live.

\- \*\*Доработка\*\*: убрал multi-stage (для Python разница минимальна, slim достаточно); добавил `init\_render.py` для пересоздания БД при старте — на Render ФС эфемерная.

\- \*\*Почему такая модель/промпт\*\*: выбрал модель, которая хорошо знает Docker и FastAPI. В промпте явно указал `$PORT` и эфемерную ФС, чтобы не получить хардкод 8000 и потерю БД.

\- \*\*Итог\*\*: в проект вошёл `Dockerfile` (slim, non-root опционально, `init\_render.py` в CMD), задеплоен на Render.



\### AI-взаимодействие №4: ревью Dockerfile



\- \*\*Дата/этап\*\*: 2026-11-10, после генерации.

\- \*\*Задача\*\*: проверить Dockerfile на безопасность, размер, кеш.

\- \*\*Модель\*\*: DEEPSEEKv3.

\- \*\*Промпт\*\*: «Вот мой Dockerfile. Проведи критическое ревью по пунктам: безопасность, размер образа, кеширование слоёв, порты, права пользователя, секреты, health-check, обработка переменных окружения. Для каждого замечания — что не так и как исправить. \[вставлен Dockerfile]».

\- \*\*Контекст\*\*: мой Dockerfile целиком.

\- \*\*Результат\*\*: модель предложила добавить `.dockerignore`, использовать `--no-cache-dir`, зафиксировать версии пакетов, добавить `USER appuser`, HEALTHCHECK.

\- \*\*Проверка\*\*: сравнил с официальной документацией Docker и FastAPI; проверил, что `--no-cache-dir` уже есть, версии в `requirements.txt` зафиксированы.

\- \*\*Доработка\*\*: добавил `.dockerignore` (исключил `.venv`, `\_\_pycache\_\_`, `\*.db`, `.git`). Остальное отклонил: `USER appuser` для учебного проекта не критично, HEALTHCHECK на Render Free не нужен (есть `/health`).

\- \*\*Почему такая модель/промпт\*\*: та же модель, что и для генерации, чтобы не смешивать стили. В промпте перечислил конкретные пункты ревью — иначе модель даёт общие советы.

\- \*\*Итог\*\*: добавлен `.dockerignore`. Остальные замечания задокументированы как «проверено, отклонено по причине…».

## ЛР №9. Тестирование

### AI-взаимодействие №5: генерация тест-кейсов

- **Дата/этап**: 2026-11-14, перед прогоном.
- **Задача**: получить черновик тест-кейсов по требованиям к API.
- **Модель**: deepseekv3.
- **Почему выбран этот вариант**: модель хорошо знает REST-конвенции; в промпте явно указал эндпоинты, модель данных и коды, чтобы не получить общий ответ.
- **Полный промпт**:Ты — QA-инженер. Изучи требования к системе учёта заявок:
- REST API на FastAPI: /api/requests (GET список, GET по id, POST создание, PATCH, DELETE), /api/requests/{id}/status, /api/requests/{id}/assign, /api/requests/{id}/comments, /api/users, /api/categories, /api/statuses, /health
- Модель данных: заявка (title, description, category_id, status_id, applicant_id, executor_id), статусы (Новая, В работе, Выполнена, Закрыта), категории, пользователи с ролями (admin, operator, executor, applicant), комментарии
- Валидация: title обязателен (1–200 символов), category/status/applicant должны существовать, исполнитель должен иметь роль executor
- HTTP-коды: 200, 201, 204, 404, 422

Составь тест-кейсы с ID, категорией (позитивный/негативный/граничный/интеграционный/API), целью, входными данными, ожидаемым результатом. Не придумывай функции, которых нет. Формат — таблица Markdown..
- **Самостоятельная проверка**: прогнал все 22 кейса через curl (`testing/lab9/test_cases.md`), 22 PASS, 0 FAIL.
- **Вклад студента**: адаптировал кейсы под реальные эндпоинты, добавил интеграционные TC-18/TC-19.

### AI-взаимодействие №6: ревью тест-кейсов

- **Дата/этап**: 2026-11-14, после составления набора.
- **Задача**: проверить полноту набора.
- **Модель**:deepseekv3.
- **Почему выбран этот вариант**: нужен критический взгляд на покрытие.
- **Полный промпт**: Вот мой набор из 22 тест-кейсов. Проведи ревью: какие негативные, граничные и интеграционные сценарии пропущены? Что стоит добавить? Какие кейсы избыточны?.
- **Краткий результат**: Общая оценка
Набор покрывает «счастливый путь» и базовые негативы, но имеет заметные пробелы в областях: PATCH-обновление, валидация полей applicant/executor при создании, контрактные проверки тела ответа, идемпотентность/порядок статусов, границы других полей (не только title), а также негативы на уровне HTTP-методов и маршрутов. Также есть несколько кейсов, которые дублируют друг друга или проверяют не то, что заявлено в цели..
- **Что принято/отклонено**: объединил в один параметризованный кейс «GET /api/requests с фильтрами..

## ЛР №10. Автоматизация тестов

### AI-взаимодействие №7: генерация автотестов

- **Дата/этап**: 2026-11-14, перед написанием `testing/lab10/test_api.py`.
- **Задача**: получить черновик pytest-тестов для FastAPI-проекта.
- **Модель**: deepseekv3
- **Почему выбран этот вариант**: модель хорошо знает pytest + FastAPI; в промпте явно указал TestClient, in-memory SQLite, StaticPool и категории тестов, чтобы не получить общий ответ.
- **Полный промпт**:Тест упал с ошибкой:
sqlite3.OperationalError: no such table: Requests
Контекст: pytest, FastAPI TestClient, in-memory SQLite. Фикстура db_engine создаёт engine = create_engine("sqlite:///:memory:"), наполняет из schema.sql + seed.sql. Тесты бизнес-логики (db_session) проходят, а тесты API (client) падают с "no such table". .
- **Самостоятельная проверка**: `python -m pytest testing/lab10/test_api.py -v` → 16 passed. Лог в `testing/lab10/test_run.txt`.
- **Вклад студента**: адаптировал тесты под реальный API, добавил фикстуру `client` с `StaticPool`.

### AI-взаимодействие №8: диагностика упавшего теста

- **Дата/этап**: 2026-11-14, при отладке тестов API.
- **Задача**: понять, почему `client` видит пустую БД (`no such table: Requests`), а `db_session` — нет.
- **Модель**: deepseekv3
- **Почему выбран этот вариант**: нужна диагностика конкретной ошибки.
- **Полный промпт**:Ты — QA-инженер. Предложи черновики автотестов на pytest для FastAPI-проекта «Система учёта заявок».
Контекст:
- FastAPI + SQLAlchemy + SQLite
- Эндпоинты: GET /api/requests, GET /api/requests/{id}, POST /api/requests, PATCH /api/requests/{id}, DELETE /api/requests/{id}, POST /api/requests/{id}/status, POST /api/requests/{id}/assign, POS .
- **Краткий результат**: [что предложила модель — например, «каждый create_engine(":memory:") создаёт новую БД; используйте StaticPool»].
- **Что принято/отклонено**: принял `StaticPool`; отклонил предложение перейти на файловую тестовую БД (медленнее, не нужно).
- **Самостоятельная проверка**: после добавления `poolclass=StaticPool` — 16 passed.
- **Вклад студента**: применил фикс, перезапустил полный набор (не только упавший тест).
