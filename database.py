import sqlite3
import os

DB_PATH = os.path.join("data", "schedule.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            subject TEXT,
            start_time TEXT,
            end_time TEXT,
            type TEXT,
            room TEXT,
            color TEXT DEFAULT '#00a7e5'
        )
    """)
    conn.commit()
    conn.close()