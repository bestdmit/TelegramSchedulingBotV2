CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    roles TEXT DEFAULT '',
    subjects TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY,
    user_id BIGINT,
    user_role TEXT NOT NULL,
    subjects TEXT NOT NULL,
    event_date VARCHAR(10),
    event_time VARCHAR(11),
    time_type VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);