"""
Ініціалізація бази даних
"""

import sqlite3
import os


DB_PATH = os.path.join("src/data", "schedule.db")


def init_db() -> None:
    """Ініціалізує базу даних, створюючи таблицю lessons, якщо її немає."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            type TEXT,
            room TEXT,
            color TEXT DEFAULT '#00a7e5'
        )
    """)
    conn.commit()
    conn.close()
