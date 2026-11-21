
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone

from services.research_history_store import DB_PATH


def init_auth_tokens_db() -> None:
    """Create the authentication token table if needed."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                purpose TEXT NOT NULL
                    CHECK (purpose IN ('email_verification', 'password_reset')),
                expires_at TEXT NOT NULL,
                used_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_purpose
            ON auth_tokens (user_id, purpose)
        """)

        connection.commit()


def save_auth_token(
    user_id: int,
    token_hash: str,
    purpose: str,
    expires_at: str,
) -> int:
    """Save a verification or password-reset token."""

    if purpose not in ("email_verification", "password_reset"):
        raise ValueError("Invalid token purpose.")

    with closing(sqlite3.connect(DB_PATH)) as connection:
        # SQLite requires foreign-key enforcement per connection.
        connection.execute("PRAGMA foreign_keys = ON")

        cursor = connection.execute(
            """
            INSERT INTO auth_tokens (
                user_id,
                token_hash,
                purpose,
                expires_at,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                token_hash,
                purpose,
                expires_at,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.commit()
        return cursor.lastrowid


def get_auth_token(
    token_hash: str,
    purpose: str,
) -> dict | None:
    """Find a saved authentication token by its fingerprint."""

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT id, user_id, token_hash,
                   purpose, expires_at, used_at
            FROM auth_tokens
            WHERE token_hash = ? AND purpose = ?
            """,
            (token_hash, purpose),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def redeem_verification_token(token_hash: str) -> bool:
    """Activate a user and consume a valid ticket atomically."""

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        # Acquire the write lock before checking the ticket.
        connection.execute("BEGIN IMMEDIATE")

        token = connection.execute(
            """
            SELECT id, user_id
            FROM auth_tokens
            WHERE token_hash = ?
              AND purpose = 'email_verification'
              AND used_at IS NULL
              AND expires_at > ?
            """,
            (token_hash, now),
        ).fetchone()

        if token is None:
            connection.rollback()
            return False

        # Activate the account belonging to this ticket.
        updated = connection.execute(
            """
            UPDATE users
            SET is_verified = 1,
                updated_at = ?
            WHERE id = ?
              AND disabled = 0
            """,
            (now, token[1]),
        )

        if updated.rowcount != 1:
            connection.rollback()
            return False

        # Mark the ticket as used.
        consumed = connection.execute(
            """
            UPDATE auth_tokens
            SET used_at = ?
            WHERE id = ?
              AND used_at IS NULL
            """,
            (now, token[0]),
        )

        if consumed.rowcount != 1:
            connection.rollback()
            return False

        connection.commit()
        return True

def save_verification_token_with_cooldown(
    user_id: int,
    token_hash: str,
    expires_at: str,
) -> bool:
    """Save a resend token only when the account is eligible."""

    now = datetime.now(timezone.utc)
    cooldown_start = (
        now - timedelta(minutes=2)
    ).isoformat()

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        # Lock before checking, so simultaneous requests
        # cannot both pass the cooldown check.
        connection.execute("BEGIN IMMEDIATE")

        # Check whether the account can be verified.
        user = connection.execute(
            """
            SELECT is_verified, disabled
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None or user[0] or user[1]:
            connection.rollback()
            return False

        # Check whether a verification token was
        # created during the last two minutes.
        recent_token = connection.execute(
            """
            SELECT 1
            FROM auth_tokens
            WHERE user_id = ?
              AND purpose = 'email_verification'
              AND created_at > ?
            LIMIT 1
            """,
            (user_id, cooldown_start),
        ).fetchone()

        if recent_token is not None:
            connection.rollback()
            return False

        # Save a fresh verification token.
        connection.execute(
            """
            INSERT INTO auth_tokens (
                user_id,
                token_hash,
                purpose,
                expires_at,
                created_at
            )
            VALUES (?, ?, 'email_verification', ?, ?)
            """,
            (
                user_id,
                token_hash,
                expires_at,
                now.isoformat(),
            ),
        )

        connection.commit()
        return True
