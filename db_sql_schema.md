-- Schema for points.sqlite

CREATE TABLE points (
    id INTEGER PRIMARY KEY,
    lat REAL,
    lon REAL,
    rating INTEGER,
    country TEXT,
    wait INTEGER,
    name TEXT,
    comment TEXT,
    datetime TEXT,
    reviewed BOOLEAN,
    banned BOOLEAN,
    ip TEXT,
    dest_lat REAL,
    dest_lon REAL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE duplicates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT,
    ip TEXT,
    reviewed BOOLEAN,
    accepted BOOLEAN,
    from_lat REAL,
    from_lon REAL,
    to_lat REAL,
    to_lon REAL
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    username TEXT UNIQUE,
    active BOOLEAN,
    confirmed_at TEXT
);

CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    description TEXT
);

CREATE TABLE roles_users (
    user_id INTEGER,
    role_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(role_id) REFERENCES roles(id)
);
