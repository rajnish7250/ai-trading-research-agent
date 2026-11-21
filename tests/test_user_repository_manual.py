
import sqlite3
import tempfile
from pathlib import Path

import auth.user_repository as repo
from auth.password import hash_password, verify_password


def main():
    original_db_path = repo.DB_PATH

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo.DB_PATH = Path(temp_dir) / "practice_users.db"

            repo.init_users_db()

            password_hash = hash_password("PracticePassword123!")

            user_id = repo.create_user(
                email=" STUDENT@example.com ",
                full_name="Practice Student",
                hashed_password=password_hash,
            )

            user = repo.get_user_by_email("student@example.com")

            assert user is not None
            assert user["id"] == user_id
            assert user["email"] == "student@example.com"
            assert user["full_name"] == "Practice Student"
            assert user["is_verified"] is False
            assert user["disabled"] is False

            assert verify_password(
                "PracticePassword123!",
                user["hashed_password"],
            )

            missing_user = repo.get_user_by_email(
                "unknown@example.com"
            )

            assert missing_user is None

            print("User lookup: PASSED")
            print("Email normalization: PASSED")
            print("Password verification: PASSED")
            print("Unknown user lookup: PASSED")

    finally:
        repo.DB_PATH = original_db_path


if __name__ == "__main__":
    main()
