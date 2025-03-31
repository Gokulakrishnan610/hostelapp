-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Create Students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female')),
    email TEXT UNIQUE NOT NULL,
    password TEXT DEFAULT 'changeme@123',
    room_id INTEGER,
    payment_status TEXT DEFAULT 'No Request' 
        CHECK (payment_status IN ('Pending', 'Confirmed', 'Failed', 'No Request')),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Create Rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    menu TEXT NOT NULL CHECK (menu IN ('Veg', 'Non Veg')),
    rooms_count INTEGER NOT NULL,
    pax_per_room INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    available_seats INTEGER NOT NULL
);

-- Create Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'No Request' 
        CHECK (status IN ('Pending', 'Confirmed', 'Failed', 'No Request')),
    admin_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Insert Boys' Hostel data
INSERT INTO rooms (category, location, menu, rooms_count, pax_per_room, capacity, available_seats) VALUES
    ('2 AC A', 'BH2', 'Veg', 30, 2, 60, 60),
    ('3 Non AC C', 'Thandalam', 'Non Veg', 2, 3, 6, 6),
    ('4 AC A', 'BH2', 'Veg', 79, 4, 316, 316),
    ('4 Non AC A', 'Habitat', 'Non Veg', 152, 4, 608, 608),
    ('5 Non AC C', 'Thandalam', 'Non Veg', 27, 5, 135, 135),
    ('6 Non AC C', 'Habitat', 'Non Veg', 240, 6, 1440, 1440);

-- Insert Girls' Hostel data
INSERT INTO rooms (category, location, menu, rooms_count, pax_per_room, capacity, available_seats) VALUES
    ('2 AC A', 'GH1 (BH3)', 'Veg', 6, 2, 12, 12),
    ('2 AC A', 'GH2', 'Veg', 27, 2, 54, 54),
    ('2 AC A', 'GH3 (BH1)', 'Veg', 6, 2, 12, 12),
    ('2 Non AC C', 'GH1 (BH3)', 'Veg', 118, 2, 236, 236),
    ('2 Non AC C', 'GH3 (BH1)', 'Veg', 43, 2, 86, 86),
    ('3 AC A', 'GH3 (BH1)', 'Veg', 18, 3, 36, 36),
    ('3 Non AC C', 'GH3 (BH1)', 'Veg', 80, 3, 240, 240),
    ('4 Non AC C', 'GH3 (BH1)', 'Veg', 76, 4, 304, 304),
    ('4 Non AC C', 'GH2', 'Veg', 178, 4, 712, 712),
    ('6 Non AC C', 'GH1 (BH3)', 'Veg', 13, 6, 78, 78); 