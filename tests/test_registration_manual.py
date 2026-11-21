
import sqlite3
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import auth.user_repository as repo
from auth.registration_service import register_user
from auth.service import authenticate_user
from auth.password import verify_password


def main():
    original_db_path = repo.DB_PATH

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo.DB_PATH = Path(temp_dir) / "test_registration.db"
            repo.init_users_db()

            user_id = register_user(
                email=" STUDENT@example.com ",
                full_name="Practice Student",
                password="PracticePassword123!",
            )

            user = repo.get_user_by_email("student@example.com")

            assert user is not None
            assert user["id"] == user_id
            assert user["email"] == "student@example.com"
            assert user["is_verified"] is False
            assert verify_password(
                "PracticePassword123!",
                user["hashed_password"],
            )

            print("User registration: PASSED")
            print("Password hashing: PASSED")

            assert authenticate_user(
                "student@example.com",
                "PracticePassword123!",
            ) is None

            print("Unverified login blocked: PASSED")

            try:
                register_user(
                    "student@example.com",
                    "Duplicate Student",
                    "AnotherPassword123!",
                )
            except ValueError:
                print("Duplicate registration blocked: PASSED")
            else:
                raise AssertionError(
                    "Duplicate registration was not blocked"
                )

            count = sqlite3.connect(repo.DB_PATH)
            try:
                total = count.execute(
                    "SELECT COUNT(*) FROM users"
                ).fetchone()[0]
            finally:
                count.close()

            assert total == 1
            print("Only one account saved: PASSED")

    finally:
        repo.DB_PATH = original_db_path


if __name__ == "__main__":
    main()
