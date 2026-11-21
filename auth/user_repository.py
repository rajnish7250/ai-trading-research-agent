
import sqlite3
from datetime import datetime, timezone
from contextlib import closing

from services.research_history_store import DB_PATH


def init_users_db() -> None:
    """Create the registered users table if it does not exist."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                full_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                is_verified INTEGER NOT NULL DEFAULT 0
                    CHECK (is_verified IN (0, 1)),
                disabled INTEGER NOT NULL DEFAULT 0
                    CHECK (disabled IN (0, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()

def create_user(
    email: str,
    full_name: str,
    hashed_password: str,
) -> int:
    """Save a new registered user and return their ID."""

    normalized_email = email.strip().lower()
    normalized_name = full_name.strip()

    if not normalized_email or not normalized_name:
        raise ValueError("Email and full name are required.")

    if not hashed_password:
        raise ValueError("Password hash is required.")

    created_at = datetime.now(timezone.utc).isoformat()

    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (
                email,
                full_name,
                hashed_password,
                is_verified,
                disabled,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, 0, 0, ?, ?)
            """,
            (
                normalized_email,
                normalized_name,
                hashed_password,
                created_at,
                created_at,
            ),
        )
        connection.commit()
        return cursor.lastrowid


def get_user_by_email(email: str) -> dict | None:
    """Find a registered user by email."""

    normalized_email = email.strip().lower()

    if not normalized_email:
        return None

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT
                id,
                email,
                full_name,
                hashed_password,
                is_verified,
                disabled
            FROM users
            WHERE email = ?
            """,
            (normalized_email,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "hashed_password": row["hashed_password"],
        "is_verified": bool(row["is_verified"]),
        "disabled": bool(row["disabled"]),
    }
