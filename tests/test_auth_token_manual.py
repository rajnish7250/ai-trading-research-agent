
import sqlite3
import tempfile
from pathlib import Path
from contextlib import closing

import auth.user_repository as user_repo
import auth.token_repository as token_repo

from auth.token_service import generate_verification_token


def main():
    original_user_db = user_repo.DB_PATH
    original_token_db = token_repo.DB_PATH

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "test_auth_tokens.db"

            # Both repositories use the same practice database.
            user_repo.DB_PATH = test_db
            token_repo.DB_PATH = test_db

            # Create the practice tables.
            user_repo.init_users_db()
            token_repo.init_auth_tokens_db()

            # Create a practice student.
            user_id = user_repo.create_user(
                email="ticket-test@example.invalid",
                full_name="Ticket Test Student",
                hashed_password="test-hash-only",
            )

            # Generate a secure verification ticket.
            raw_token, token_hash, expires_at = (
                generate_verification_token()
            )

            # Save only the ticket fingerprint.
            token_id = token_repo.save_auth_token(
                user_id=user_id,
                token_hash=token_hash,
                purpose="email_verification",
                expires_at=expires_at,
            )

            with closing(sqlite3.connect(test_db)) as connection:
                saved = connection.execute(
                    """
                    SELECT user_id, token_hash, purpose, expires_at
                    FROM auth_tokens
                    WHERE id = ?
                    """,
                    (token_id,),
                ).fetchone()

            assert saved is not None
            assert saved[0] == user_id
            assert saved[1] == token_hash
            assert saved[2] == "email_verification"
            assert saved[3] == expires_at

            print("Verification ticket saved: PASSED")


            # Find the ticket using its fingerprint.
            found = token_repo.get_auth_token(
                token_hash=token_hash,
                purpose="email_verification",
            )

            assert found is not None
            assert found["id"] == token_id
            assert found["user_id"] == user_id
            assert found["token_hash"] == token_hash

            print("Ticket lookup: PASSED")

            # An unknown ticket should not be found.
            missing = token_repo.get_auth_token(
                token_hash="unknown-ticket-fingerprint",
                purpose="email_verification",
            )

            assert missing is None

            print("Unknown ticket rejected: PASSED")


            # The original secret must not be in the database.
            assert raw_token not in saved

            print("Raw ticket not stored: PASSED")

            # A nonexistent student must not receive a ticket.
            try:
                token_repo.save_auth_token(
                    user_id=999999,
                    token_hash="nonexistent-user-test-hash",
                    purpose="email_verification",
                    expires_at=expires_at,
                )
            except sqlite3.IntegrityError:
                print("Nonexistent user rejected: PASSED")
            else:
                raise AssertionError(
                    "Foreign-key protection failed"
                )

            # Check the practice database is healthy.
            with closing(sqlite3.connect(test_db)) as connection:
                health = connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()[0]

            assert health == "ok"
            print("Practice database health: PASSED")

    finally:
        user_repo.DB_PATH = original_user_db
        token_repo.DB_PATH = original_token_db




if __name__ == "__main__":
    main()
