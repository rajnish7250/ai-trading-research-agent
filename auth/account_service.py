"""Password recovery and account management for registered users."""

import hashlib
import logging
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from html import escape
from threading import Lock

from auth.email_service import send_email
from auth.password import hash_password, validate_new_password, verify_password
from auth.service import get_user
from auth.token_service import generate_auth_token
from auth.verification_link import build_public_token_url
from services.research_history_store import DB_PATH, init_db

logger = logging.getLogger(__name__)

# The API runs with one worker. Share these locks with research so an
# in-flight graph cannot recreate account data after successful deletion.
_account_locks = [Lock() for _ in range(64)]


def account_lock(email: str):
    return _account_locks[hash(email) % len(_account_locks)]


def _store_reset_token(user_id: int, token_hash: str, expires_at: str) -> bool:
    now = datetime.now(timezone.utc)
    with closing(sqlite3.connect(DB_PATH)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        return connection.execute(
            """
            INSERT INTO auth_tokens
                (user_id, token_hash, purpose, expires_at, created_at)
            SELECT id, ?, 'password_reset', ?, ? FROM users
            WHERE id = ? AND is_verified = 1 AND disabled = 0
              AND NOT EXISTS (
                  SELECT 1 FROM auth_tokens
                  WHERE user_id = users.id AND purpose = 'password_reset'
                    AND created_at > ?
              )
            """,
            (token_hash, expires_at, now.isoformat(), user_id,
             (now - timedelta(minutes=2)).isoformat()),
        ).rowcount == 1


def send_account_email(email: str, subject: str, body: str) -> bool:
    try:
        send_email(to_email=email, subject=subject, html_body=body)
    except Exception:
        logger.warning("Account email delivery failed.")
        return False
    return True


def request_password_reset(email: str) -> None:
    email = email.strip().lower()
    user = get_user(email)
    if not user or "id" not in user:
        return

    raw_token, token_hash, expires_at = generate_auth_token(minutes=30)
    try:
        url = build_public_token_url("reset_token", raw_token)
    except (RuntimeError, ValueError):
        logger.warning("Password reset link configuration is invalid.")
        return

    if not _store_reset_token(user["id"], token_hash, expires_at):
        return

    if not send_account_email(
        email,
        "Reset your AI Trading Research password",
        f'<p><a href="{escape(url, quote=True)}">Reset password</a></p>'
        "<p>This link expires in 30 minutes. If you did not request it, ignore this email.</p>",
    ):
        with closing(sqlite3.connect(DB_PATH)) as connection, connection:
            connection.execute("DELETE FROM auth_tokens WHERE token_hash = ?", (token_hash,))


def reset_password(raw_token: str, password: str) -> str | None:
    """Consume the reset links and revoke sessions in the password update transaction."""
    validate_new_password(password)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    with closing(sqlite3.connect(DB_PATH)) as connection, connection:
        token = connection.execute(
            "SELECT 1 FROM auth_tokens WHERE token_hash = ? AND purpose = 'password_reset'"
            " AND used_at IS NULL AND expires_at > ?",
            (token_hash, datetime.now(timezone.utc).isoformat()),
        ).fetchone()
        if not token:
            return None

        password_hash = hash_password(password)
        connection.execute("BEGIN IMMEDIATE")
        now = datetime.now(timezone.utc).isoformat()
        user = connection.execute(
            """
            UPDATE users
            SET hashed_password = ?, session_version = session_version + 1, updated_at = ?
            WHERE is_verified = 1 AND disabled = 0 AND id = (
                SELECT user_id FROM auth_tokens
                WHERE token_hash = ? AND purpose = 'password_reset'
                  AND used_at IS NULL AND expires_at > ?
            )
            RETURNING id, email
            """,
            (password_hash, now, token_hash, now),
        ).fetchone()
        if not user:
            return None
        connection.execute(
            "UPDATE auth_tokens SET used_at = ? WHERE user_id = ?"
            " AND purpose = 'password_reset' AND used_at IS NULL",
            (now, user[0]),
        )
        return user[1]


def update_name(user: dict, name: str) -> bool:
    with closing(sqlite3.connect(DB_PATH)) as connection, connection:
        return connection.execute(
            "UPDATE users SET full_name = ?, updated_at = ?"
            " WHERE id = ? AND session_version = ? AND disabled = 0",
            (name, datetime.now(timezone.utc).isoformat(), user["id"], user["session_version"]),
        ).rowcount == 1


def delete_account(user: dict, password: str, clear_research_memory) -> bool:
    """Delete the account and its research under the same lock as research writes."""
    email = user["email"]
    with account_lock(email):
        current = get_user(email)
        if (
            not current
            or current.get("id") != user["id"]
            or current.get("session_version") != user["session_version"]
            or len(password.encode("utf-8")) > 72
            or not verify_password(password, current["hashed_password"])
        ):
            return False

        init_db()
        with closing(sqlite3.connect(DB_PATH)) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            if connection.execute(
                "DELETE FROM users WHERE id = ? AND session_version = ?",
                (user["id"], user["session_version"]),
            ).rowcount != 1:
                return False
            connection.execute("DELETE FROM auth_tokens WHERE user_id = ?", (user["id"],))
            connection.execute("DELETE FROM research_history WHERE user_id = ?", (email,))
            clear_research_memory(email)
        return True
