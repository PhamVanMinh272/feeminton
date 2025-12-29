

-- Example seed data
INSERT INTO members (name, gender) VALUES
('Minh', 'male'),
('Đạt', 'male'),
('Thiên', 'male'),
('Tâm', 'male'),
('Tấn', 'male'),
('Thoại', 'male'),
('Giao', 'female'),
('Ân', 'female');

INSERT INTO reservations (date, court_count) VALUES
('2025-01-05', 4),
('2025-01-12', 4),
('2025-01-19', 4),
('2025-01-26', 4);

-- Default attendance (everyone joins)
INSERT INTO attendance (reservation_id, member_id, joined)
SELECT r.id, m.id, 1
FROM reservations r, members m;