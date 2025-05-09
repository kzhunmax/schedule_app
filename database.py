import sqlite3
import os

DB_PATH = os.path.join("data", "schedule.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            time TEXT,
            type TEXT NOT NULL,
            room TEXT
        )
    """)
    conn.commit()
    conn.close()