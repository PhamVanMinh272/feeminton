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


-- Insert schedules for group 1 (first Tuesdays)
INSERT INTO schedules (group_id, schedule_date) VALUES
(1, '2026-01-06'),
(1, '2026-02-03'),
(1, '2026-03-03'),
(1, '2026-04-07'),
(1, '2026-05-05'),
(1, '2026-06-02'),
(1, '2026-07-07'),
(1, '2026-08-04'),
(1, '2026-09-01'),
(1, '2026-10-06'),
(1, '2026-11-03'),
(1, '2026-12-01');

-- Insert schedules for group 2 (first Thursdays)
INSERT INTO schedules (group_id, schedule_date) VALUES
(2, '2026-01-01'),
(2, '2026-02-05'),
(2, '2026-03-05'),
(2, '2026-04-02'),
(2, '2026-05-07'),
(2, '2026-06-04'),
(2, '2026-07-02'),
(2, '2026-08-06'),
(2, '2026-09-03'),
(2, '2026-10-01'),
(2, '2026-11-05'),
(2, '2026-12-03');
