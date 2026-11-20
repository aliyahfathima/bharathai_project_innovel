import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / ".bharat_scheme.db"

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                state TEXT,
                need TEXT,
                profile_summary TEXT,
                result_count INTEGER
            )
        """)

def save_search(profile, count):
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO searches(created_at,state,need,profile_summary,result_count) VALUES(?,?,?,?,?)",
            (datetime.now().isoformat(timespec="seconds"), profile.state, profile.need,
             f"Age={profile.age}; income={profile.annual_income}; occupation={profile.occupation}", count)
        )

def recent_searches(limit=10):
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        return con.execute(
            "SELECT created_at,state,need,result_count FROM searches ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
