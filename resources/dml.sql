INSERT INTO groups (name) VALUES ('Chan Dong Original (Thu 4)'), ('Group Thu 6');

-- Example seed data
INSERT INTO users (name, gender) VALUES
('Minh', 'male'),
('Đạt', 'male'),
('Thiên', 'male'),
('Tâm', 'male'),
('Tấn', 'male'),
('Thoại', 'male'),
('Giao', 'female'),
('Ân', 'female'),
('Thảo', 'female'),
('Trí', 'male'),
('Nghị', 'male'),
('Tú', 'female');

INSERT INTO members (group_id, user_id, nickname, member_fee) VALUES
(1, 1, 'Minh', 50),
(1, 2, 'Đạt', 50),
(1, 9, 'Thảo', 50),
(1, 10, 'Trí', 50),
(1, 11, 'Nghị', 50),
(1, 12, 'Tú', 50),
(2, 1, 'Minh', 60),
(2, 2, 'Đạt', 60),
(2, 3, 'Thiên', 60),
(2, 4, 'Tâm', 60),
(2, 5, 'Tấn', 60),
(2, 6, 'Thoại', 60),
(2, 7, 'Giao', 50),
(2, 8, 'Ân', 50);


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
