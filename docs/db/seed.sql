-- seed.sql: тестовые данные
INSERT INTO Users (full_name, email, role) VALUES
('Админ Админов', 'admin@example.com', 'admin'),
('Оператор Операторов', 'operator@example.com', 'operator'),
('Исполнитель Иванов', 'ivanov@example.com', 'executor'),
('Заявитель Петров', 'petrov@example.com', 'applicant'),
('Исполнитель Сидоров', 'sidorov@example.com', 'executor');

INSERT INTO Categories (name) VALUES
('Оборудование'), ('Программное обеспечение'), ('Доступы'), ('Прочее');

INSERT INTO Statuses (name) VALUES
('Новая'), ('В работе'), ('Выполнена'), ('Закрыта');

INSERT INTO Requests (title, description, category_id, status_id, applicant_id, executor_id) VALUES
('Не работает принтер', 'Принтер в офисе 305 не печатает', 1, 1, 4, NULL),
('Нет доступа к папке', 'Нужен доступ к сетевой папке проекта', 3, 2, 4, 3),
('Установить программу', 'Установить Excel на новый ноутбук', 2, 3, 4, 3),
('Заменить картридж', 'Закончился тонер в принтере', 1, 1, 4, NULL),
('Настроить VPN', 'Не подключается VPN из дома', 3, 2, 4, 5);

INSERT INTO Comments (request_id, user_id, text) VALUES
(2, 3, 'Выехал, буду через 20 минут'),
(2, 4, 'Спасибо, жду'),
(3, 3, 'Программа установлена'),
(5, 5, 'Проверяю настройки');