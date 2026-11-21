
import tempfile
from pathlib import Path

import auth.user_repository as user_repo
import auth.token_repository as token_repo

from auth.verification_service import (
    issue_verification_token,
    verify_email_token,
)


def main():
    original_user_db = user_repo.DB_PATH
    original_token_db = token_repo.DB_PATH

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "verification_service_test.db"

            # Use only our temporary practice database.
            user_repo.DB_PATH = test_db
            token_repo.DB_PATH = test_db

            user_repo.init_users_db()
            token_repo.init_auth_tokens_db()

            # Create a fictional student.
            user_id = user_repo.create_user(
                email="service-test@example.invalid",
                full_name="Service Test Student",
                hashed_password="test-hash-only",
            )

            user = user_repo.get_user_by_email(
                "service-test@example.invalid"
            )

            assert user["is_verified"] is False
            print("User initially unverified: PASSED")

            # Issue a ticket through our verification service.
            raw_token = issue_verification_token(user_id)

            assert isinstance(raw_token, str)
            assert len(raw_token) >= 32
            print("Verification ticket issued: PASSED")

            # Use the ticket to verify the email.
            assert verify_email_token(raw_token) is True

            user = user_repo.get_user_by_email(
                "service-test@example.invalid"
            )

            assert user["is_verified"] is True
            print("Email verification successful: PASSED")

            # The same ticket must not work twice.
            assert verify_email_token(raw_token) is False
            print("Ticket reuse blocked: PASSED")

            # A fake ticket must fail.
            assert verify_email_token("fake-ticket") is False
            print("Fake ticket rejected: PASSED")

            # Invalid input must fail.
            assert verify_email_token("") is False
            assert verify_email_token(None) is False
            print("Invalid token input rejected: PASSED")

    finally:
        user_repo.DB_PATH = original_user_db
        token_repo.DB_PATH = original_token_db


if __name__ == "__main__":
    main()
