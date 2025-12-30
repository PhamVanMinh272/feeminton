INSERT INTO groups (name) VALUES ('Group Thu 4'), ('Group Thu 6');

-- Example seed data
INSERT INTO users (name, gender) VALUES
('Minh', 'male'),
('Đạt', 'male'),
('Thiên', 'male'),
('Tâm', 'male'),
('Tấn', 'male'),
('Thoại', 'male'),
('Giao', 'female'),
('Ân', 'female');

INSERT INTO members (group_id, user_id, nickname) VALUES
(1, 1, 'Minh'),
(1, 2, 'Đạt'),
(1, 3, 'Thiên'),
(1, 4, 'Tâm'),
(2, 5, 'Tấn'),
(2, 6, 'Thoại'),
(2, 7, 'Giao'),
(2, 8, 'Ân');

INSERT INTO reservations (date, court_count) VALUES
('2025-01-05', 4),
('2025-01-12', 4),
('2025-01-19', 4),
('2025-01-26', 4);

-- Default attendance (everyone joins)
INSERT INTO attendance (reservation_id, member_id, joined)
SELECT r.id, m.id, 1
FROM reservations r, members m;