DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS infos;
DROP TABLE IF EXISTS lists;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users_users;
DROP TABLE IF EXISTS lists_items;
DROP TABLE IF EXISTS lists_users;
DROP TABLE IF EXISTS items_users;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users_users (
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    status CHECK(status IN ('PENDING', 'ACCEPTED', 'REJECTED', 'IGNORED')) NOT NULL,
    FOREIGN KEY (sender_id) 
        REFERENCES users (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION,
    FOREIGN KEY (receiver_id) 
        REFERENCES users (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS infos (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    description TEXT,
    avatar_url TEXT UNIQUE,
    avatar_thumb_url TEXT UNIQUE,
    avatar_medium_url TEXT UNIQUE,
    delete_avatar_url TEXT UNIQUE,
    FOREIGN KEY (user_id) 
        REFERENCES users (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS lists (
    id INTEGER NOT NULL PRIMARY KEY,
    creator_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    list_url TEXT UNIQUE,
    list_thumb_url TEXT UNIQUE,
    list_medium_url TEXT UNIQUE,
    delete_list_url TEXT UNIQUE,
    external_link TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TEXT    
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER NOT NULL PRIMARY KEY,
    creator_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    external_link TEXT,
    type TEXT NOT NULL,
    item_url TEXT UNIQUE,
    item_thumb_url TEXT UNIQUE,
    item_medium_url TEXT UNIQUE,
    delete_item_url TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS lists_items (
    list_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    FOREIGN KEY (list_id)
        REFERENCES lists (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION,
    FOREIGN KEY (item_id)
        REFERENCES items (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS lists_users (
    list_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    right CHECK(right IN ('CREATOR', "ADMIN", "ADVANCED", "INVITED")) NOT NULL,
    FOREIGN KEY (list_id)
        REFERENCES lists (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS items_users (
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (item_id)
        REFERENCES items (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
)
