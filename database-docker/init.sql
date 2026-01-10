CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    roles TEXT DEFAULT '',
    teacher_subjects TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    user_role TEXT NOT NULL,
    subjects TEXT NOT NULL,
    event_date DATE,
    event_time TIME,
    point_type VARCHAR(255) NOT NULL,
    time_type VARCHAR(255) NOT NULL
);