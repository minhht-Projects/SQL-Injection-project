"""Creates users.db with a sample users table for the SQLi demo."""

import sqlite3

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS users")
cur.execute(
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """
)

sample_users = [
    ("admin", "password123"),
    ("alice", "sunshine99"),
    ("bob", "letmein42"),
]
cur.executemany("INSERT INTO users (username, password) VALUES (?, ?)", sample_users)

conn.commit()
conn.close()
print("users.db created with sample data:", [u[0] for u in sample_users])
