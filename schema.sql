CREATE TABLE inventory ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    item_name TEXT NOT NULL, 
    assignee TEXT NOT NULL 
);

CREATE TABLE requests (
    requestID INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    reason TEXT NOT NULL,
    assignee TEXT NOT NULL
);

CREATE TABLE users (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    userPassword TEXT NOT NULL,
    isAdmin BOOLEAN NOT NULL
);