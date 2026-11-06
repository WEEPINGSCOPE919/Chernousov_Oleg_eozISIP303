-- 5 INSERT (дополнительные)
INSERT INTO Users (full_name, email, role) VALUES ('Новый Пользователь', 'new@example.com', 'applicant');
INSERT INTO Categories (name) VALUES ('Сеть');
INSERT INTO Requests (title, description, category_id, status_id, applicant_id) VALUES ('Тестовая заявка', 'Описание', 1, 1, 4);
INSERT INTO Comments (request_id, user_id, text) VALUES (1, 4, 'Комментарий');
INSERT INTO Statuses (name) VALUES ('Отменена');

-- 5 SELECT
SELECT * FROM Users;
SELECT * FROM Requests;
SELECT * FROM Categories;
SELECT * FROM Statuses;
SELECT * FROM Comments;

-- 3 SELECT с WHERE
SELECT * FROM Requests WHERE status_id = 1;
SELECT * FROM Users WHERE role = 'executor';
SELECT * FROM Requests WHERE category_id = 1;

-- 2 UPDATE
UPDATE Requests SET status_id = 2 WHERE id = 1;
UPDATE Users SET full_name = 'Иванов Иван' WHERE id = 3;

-- 2 DELETE
DELETE FROM Comments WHERE id = 4;
DELETE FROM Requests WHERE id = 4;

-- 2 JOIN
SELECT r.id, r.title, c.name AS category, s.name AS status
FROM Requests r
JOIN Categories c ON r.category_id = c.id
JOIN Statuses s ON r.status_id = s.id;

SELECT r.id, r.title, u.full_name AS applicant
FROM Requests r
JOIN Users u ON r.applicant_id = u.id;