from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

import auth.user_repository as users
import auth.token_repository as tokens

from auth.registration_flow import register_and_issue_verification
from main import app


def main():
    # Create a temporary database for this test only.
    with TemporaryDirectory() as folder:
        test_db = Path(folder) / "verification_test.db"

        with (
            patch.object(users, "DB_PATH", test_db),
            patch.object(tokens, "DB_PATH", test_db),
        ):
            users.init_users_db()
            tokens.init_auth_tokens_db()

            # Register a temporary test user.
            _, raw_token = register_and_issue_verification(
                email="verification-test@example.com",
                full_name="Verification Test",
                password="SafeTestPassword123!",
            )

            with TestClient(app) as client:
                # First use: should succeed.
                first = client.post(
                    "/verify-email",
                    json={"token": raw_token},
                )

                # Second use: should fail.
                second = client.post(
                    "/verify-email",
                    json={"token": raw_token},
                )

            user = users.get_user_by_email(
                "verification-test@example.com"
            )

            print("First attempt:", first.status_code)
            print("Email verified:", bool(user["is_verified"]))
            print("Second attempt:", second.status_code)

            assert first.status_code == 200
            assert bool(user["is_verified"]) is True
            assert second.status_code == 400

            print("Verification API test PASSED!")


if __name__ == "__main__":
    main()