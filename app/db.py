import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List

DB_PATH = Path("data/results.sqlite")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                persons TEXT,
                dates TEXT,
                raw_text TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()

def insert_record(source: str, persons: list, dates: list, raw_text: str, created_at: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO extractions (source, persons, dates, raw_text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source, json.dumps(persons), json.dumps(dates), raw_text, created_at),
        )
        conn.commit()
        # Pylance fix: lastrowid is Optional[int]; coerce to int
        return int(cur.lastrowid or 0)

def list_records(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, source, persons, dates, raw_text, created_at
            FROM extractions
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]
