DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS infos;
DROP TABLE IF EXISTS lists;
DROP TABLE IF EXISTS items;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE infos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    description TEXT,
    avatar_url TEXT UNIQUE,
    avatar_thumb_url TEXT UNIQUE,
    avatar_medium_url TEXT UNIQUE,
    delete_avatar_url TEXT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    external_link TEXT
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    external_link TEXT,
    type TEXT NOT NULL
);

-- CREATE TABLE items_lists ()

-- CREATE TABLE users_lists ()

-- CREATE TABLE users_items ()

-- CREATE TABLE users_users ()