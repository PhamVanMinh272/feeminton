-- Users table: only store identity
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('male','female')) NOT NULL
);

-- Groups table: only store identity
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Members table: only store identity and gender
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    nickname TEXT NOT NULL
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


