import sqlite3
from pathlib import Path

DB_PATH = Path("jessica/memory/jessica_memory.db")


def init_memory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()


def remember(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO user_profile (key, value)
    VALUES (?, ?)
    """, (key, value))

    conn.commit()
    conn.close()


def recall(key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT value FROM user_profile WHERE key = ?
    """, (key,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None
