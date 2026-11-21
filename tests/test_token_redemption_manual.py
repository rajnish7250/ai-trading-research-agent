
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

import auth.user_repository as user_repo
import auth.token_repository as token_repo

from auth.token_service import generate_verification_token


def main():
    original_user_db = user_repo.DB_PATH
    original_token_db = token_repo.DB_PATH

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "verification_test.db"

            # Both repositories use our practice database.
            user_repo.DB_PATH = test_db
            token_repo.DB_PATH = test_db

            user_repo.init_users_db()
            token_repo.init_auth_tokens_db()

            # Create a fictional, unverified student.
            user_id = user_repo.create_user(
                email="verification-test@example.invalid",
                full_name="Verification Test Student",
                hashed_password="test-hash-only",
            )

            user = user_repo.get_user_by_email(
                "verification-test@example.invalid"
            )
            assert user["is_verified"] is False
            print("User initially unverified: PASSED")

            # Generate and save a valid verification ticket.
            raw_token, token_hash, expires_at = (
                generate_verification_token()
            )

            token_repo.save_auth_token(
                user_id=user_id,
                token_hash=token_hash,
                purpose="email_verification",
                expires_at=expires_at,
            )

            # First use should succeed.
            assert token_repo.redeem_verification_token(
                token_hash
            ) is True

            user = user_repo.get_user_by_email(
                "verification-test@example.invalid"
            )
            assert user["is_verified"] is True

            print("Valid ticket activates user: PASSED")

            # Ticket must now have a used_at timestamp.
            saved_token = token_repo.get_auth_token(
                token_hash,
                "email_verification",
            )

            assert saved_token["used_at"] is not None
            print("Ticket marked as used: PASSED")

            # Second use must fail.
            assert token_repo.redeem_verification_token(
                token_hash
            ) is False

            print("Ticket reuse rejected: PASSED")

            # Create a second unverified student.
            second_user_id = user_repo.create_user(
                email="expired-test@example.invalid",
                full_name="Expired Ticket Student",
                hashed_password="test-hash-only",
            )

            # Save an already-expired ticket.
            expired_at = (
                datetime.now(timezone.utc)
                - timedelta(minutes=5)
            ).isoformat()

            token_repo.save_auth_token(
                user_id=second_user_id,
                token_hash="expired-test-fingerprint",
                purpose="email_verification",
                expires_at=expired_at,
            )

            assert token_repo.redeem_verification_token(
                "expired-test-fingerprint"
            ) is False

            second_user = user_repo.get_user_by_email(
                "expired-test@example.invalid"
            )
            assert second_user["is_verified"] is False

            print("Expired ticket rejected: PASSED")

            # TEST: A disabled account must not be activated.
            disabled_user_id = user_repo.create_user(
                email="disabled-test@example.invalid",
                full_name="Disabled Test Student",
                hashed_password="test-hash-only",
            )

            with closing(sqlite3.connect(test_db)) as connection:
                connection.execute(
                    "UPDATE users SET disabled = 1 WHERE id = ?",
                    (disabled_user_id,),
                )
                connection.commit()

            _, disabled_hash, disabled_expiry = (
                generate_verification_token()
            )

            token_repo.save_auth_token(
                user_id=disabled_user_id,
                token_hash=disabled_hash,
                purpose="email_verification",
                expires_at=disabled_expiry,
            )

            assert token_repo.redeem_verification_token(
                disabled_hash
            ) is False

            disabled_user = user_repo.get_user_by_email(
                "disabled-test@example.invalid"
            )
            assert disabled_user["is_verified"] is False

            print("Disabled account rejected: PASSED")

            # TEST: A password-reset ticket cannot verify email.
            reset_user_id = user_repo.create_user(
                email="reset-test@example.invalid",
                full_name="Reset Test Student",
                hashed_password="test-hash-only",
            )

            _, reset_hash, reset_expiry = (
                generate_verification_token()
            )

            token_repo.save_auth_token(
                user_id=reset_user_id,
                token_hash=reset_hash,
                purpose="password_reset",
                expires_at=reset_expiry,
            )

            assert token_repo.redeem_verification_token(
                reset_hash
            ) is False

            reset_user = user_repo.get_user_by_email(
                "reset-test@example.invalid"
            )
            assert reset_user["is_verified"] is False

            print("Password-reset ticket rejected: PASSED")


            # Confirm the practice database is healthy.
            with closing(sqlite3.connect(test_db)) as connection:
                health = connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()[0]

            assert health == "ok"
            print("Practice database health: PASSED")

    finally:
        # Restore the original database paths.
        user_repo.DB_PATH = original_user_db
        token_repo.DB_PATH = original_token_db


if __name__ == "__main__":
    main()
