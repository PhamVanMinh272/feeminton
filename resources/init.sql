-- Members table: only store identity and gender
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('male','female')) NOT NULL
);

-- Reservations table: each reservation has a date and number of courts
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    court_count INTEGER DEFAULT 1
);

-- Attendance table: tracks who joined/unjoined each reservation
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    joined BOOLEAN DEFAULT 1,
    refund_amount INTEGER DEFAULT 0,
    FOREIGN KEY(reservation_id) REFERENCES reservations(id),
    FOREIGN KEY(member_id) REFERENCES members(id)
);

-- Refunds table: monthly aggregation of refunds per member
CREATE TABLE IF NOT EXISTS refunds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    total_refund INTEGER DEFAULT 0,
    status TEXT CHECK(status IN ('pending','sent')) DEFAULT 'pending',
    FOREIGN KEY(member_id) REFERENCES members(id)
);

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