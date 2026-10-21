
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi.encoders import jsonable_encoder


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "research_history.db"
DB_PATH = Path(os.getenv("RESEARCH_HISTORY_DB_PATH", str(DEFAULT_DB_PATH)))


def init_db():
    """Create the research history table if it does not exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS research_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                query TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_research(user_id: str, query: str, result: dict) -> int:
    """Persist one completed research result and return its ID."""
    if not user_id:
        raise ValueError("user_id is required")

    init_db()

    serialized_result = json.dumps(jsonable_encoder(result))
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO research_history
                (user_id, query, result_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, query, serialized_result, created_at),
        )
        return cursor.lastrowid


def get_research_history(user_id: str, limit: int = 20) -> list[dict]:
    """Return only the specified user's research history."""
    if not user_id:
        raise ValueError("user_id is required")

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    init_db()

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, query, result_json, created_at
            FROM research_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "query": row["query"],
            "result": json.loads(row["result_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
