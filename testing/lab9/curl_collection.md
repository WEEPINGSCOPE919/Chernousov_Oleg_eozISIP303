# Коллекция API-запросов (curl) — ЛР №9

**Базовый URL**: https://chernousov-oleg-eozisip303.onrender.com

## 1. Health-check

```bash
curl -i https://chernousov-oleg-eozisip303.onrender.com/health
```

## 2. Список заявок

```bash
curl -i https://chernousov-oleg-eozisip303.onrender.com/api/requests
```

## 3. Заявка по id

```bash
curl -i https://chernousov-oleg-eozisip303.onrender.com/api/requests/1
```

## 4. Поиск по title

```bash
curl -i "https://chernousov-oleg-eozisip303.onrender.com/api/requests?search=VPN"
```

## 5. Фильтр по статусу

```bash
curl -i "https://chernousov-oleg-eozisip303.onrender.com/api/requests?status_id=2"
```

## 6. Создание заявки (201)

```bash
cat > /tmp/body.json << 'EOF'
{"title":"Тест","description":"Описание","category_id":1,"status_id":1,"applicant_id":4}
EOF
curl -i -X POST https://chernousov-oleg-eozisip303.onrender.com/api/requests \
  -H "Content-Type: application/json" -d @/tmp/body.json
```

## 7. Смена статуса (200)

```bash
cat > /tmp/body.json << 'EOF'
{"status_id":2}
EOF
curl -i -X POST https://chernousov-oleg-eozisip303.onrender.com/api/requests/1/status \
  -H "Content-Type: application/json" -d @/tmp/body.json
```

## 8. Назначение исполнителя (200)

```bash
cat > /tmp/body.json << 'EOF'
{"user_id":3}
EOF
curl -i -X POST https://chernousov-oleg-eozisip303.onrender.com/api/requests/1/assign \
  -H "Content-Type: application/json" -d @/tmp/body.json
```

## 9. Комментарий (201)

```bash
cat > /tmp/body.json << 'EOF'
{"user_id":4,"text":"Комментарий"}
EOF
curl -i -X POST https://chernousov-oleg-eozisip303.onrender.com/api/requests/1/comments \
  -H "Content-Type: application/json" -d @/tmp/body.json
```

## 10. Удаление (204)

```bash
curl -i -X DELETE https://chernousov-oleg-eozisip303.onrender.com/api/requests/6
```

## 11. Несуществующая заявка (404)

```bash
curl -i https://chernousov-oleg-eozisip303.onrender.com/api/requests/99999
```

## 12. Невалидные данные (422)

```bash
cat > /tmp/body.json << 'EOF'
{"title":"","category_id":1,"status_id":1,"applicant_id":4}
EOF
curl -i -X POST https://chernousov-oleg-eozisip303.onrender.com/api/requests \
  -H "Content-Type: application/json" -d @/tmp/body.json
```