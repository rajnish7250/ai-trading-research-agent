
import hashlib
import tempfile
from pathlib import Path

import auth.user_repository as user_repo
import auth.token_repository as token_repo

from auth.registration_flow import (
    register_and_issue_verification,
)
from auth.verification_service import verify_email_token
from auth.password import verify_password


def main():
    original_user_db = user_repo.DB_PATH
    original_token_db = token_repo.DB_PATH

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "registration_flow_test.db"

            # Redirect both repositories to our practice DB.
            user_repo.DB_PATH = test_db
            token_repo.DB_PATH = test_db

            user_repo.init_users_db()
            token_repo.init_auth_tokens_db()

            email = "registration-flow@example.invalid"
            password = "SecurePracticePassword123!"

            # Register user and issue verification ticket.
            user_id, raw_token = (
                register_and_issue_verification(
                    email=email,
                    full_name="Practice Student",
                    password=password,
                )
            )

            assert isinstance(user_id, int)
            assert user_id > 0
            print("User registration: PASSED")

            # Check the stored user.
            user = user_repo.get_user_by_email(email)

            assert user is not None
            assert user["id"] == user_id
            assert user["is_verified"] is False
            print("User initially unverified: PASSED")

            # The real password must never be stored.
            assert user["hashed_password"] != password
            assert verify_password(
                password,
                user["hashed_password"],
            ) is True

            print("Password securely hashed: PASSED")

            # Check the verification ticket in the database.
            token_hash = hashlib.sha256(
                raw_token.encode("utf-8")
            ).hexdigest()

            saved_token = token_repo.get_auth_token(
                token_hash,
                "email_verification",
            )

            assert saved_token is not None
            assert saved_token["user_id"] == user_id
            assert saved_token["used_at"] is None

            print("Verification ticket saved: PASSED")

            # Verify the email using the issued ticket.
            assert verify_email_token(raw_token) is True

            verified_user = user_repo.get_user_by_email(
                email
            )

            assert verified_user["is_verified"] is True
            print("Email verification: PASSED")

            # Ticket cannot be used again.
            assert verify_email_token(raw_token) is False
            print("Ticket reuse blocked: PASSED")

    finally:
        # Restore original database paths.
        user_repo.DB_PATH = original_user_db
        token_repo.DB_PATH = original_token_db


if __name__ == "__main__":
    main()
