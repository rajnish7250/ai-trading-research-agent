import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app, limiter
from auth.user_repository import get_user_by_email


class RegistrationIntegrationTest(unittest.TestCase):

    def setUp(self):
        """Clear rate-limit counters before this integration test."""
        limiter._storage.reset()

    def test_complete_registration_journey(self):

        email = "integration-student@example.com"
        password = "StrongPassword123!"

        # Create an isolated temporary database.
        with TemporaryDirectory() as temp_dir:

            test_db = Path(temp_dir) / "test_auth.db"

            with (
                patch("auth.user_repository.DB_PATH", test_db),
                patch("auth.token_repository.DB_PATH", test_db),
                patch(
                    "auth.registration_flow."
                    "send_verification_email_for_token"
                ) as fake_email,
            ):

                # Starts FastAPI's normal database initialization
                # against our temporary authentication database.
                with TestClient(app) as client:

                    # TEST 1: Register a new account.
                    register_response = client.post(
                        "/register",
                        json={
                            "full_name": "Integration Student",
                            "email": email,
                            "password": password,
                        },
                    )

                    self.assertEqual(
                        register_response.status_code,
                        200,
                        register_response.text,
                    )

                    # TEST 2: Confirm email sending was requested.
                    fake_email.assert_called_once()

                    email_arguments = fake_email.call_args.kwargs

                    self.assertEqual(
                        email_arguments["to_email"],
                        email,
                    )

                    raw_token = email_arguments["raw_token"]

                    self.assertTrue(raw_token)

                    # TEST 3: User exists but is not verified.
                    user = get_user_by_email(email)

                    self.assertIsNotNone(user)
                    self.assertFalse(user["is_verified"])

                    # TEST 4: Login must fail before verification.
                    blocked_login = client.post(
                        "/login",
                        data={
                            "username": email,
                            "password": password,
                        },
                    )

                    self.assertEqual(
                        blocked_login.status_code,
                        401,
                    )

                    # TEST 5: Verify the email.
                    verify_response = client.post(
                        "/verify-email",
                        json={"token": raw_token},
                    )

                    self.assertEqual(
                        verify_response.status_code,
                        200,
                        verify_response.text,
                    )

                    verified_user = get_user_by_email(email)

                    self.assertTrue(
                        verified_user["is_verified"]
                    )

                    # TEST 6: Login should now succeed.
                    successful_login = client.post(
                        "/login",
                        data={
                            "username": email,
                            "password": password,
                        },
                    )

                    self.assertEqual(
                        successful_login.status_code,
                        200,
                        successful_login.text,
                    )

                    self.assertIn(
                        "access_token",
                        successful_login.json(),
                    )

                    # TEST 7: Verification token cannot be reused.
                    replay_response = client.post(
                        "/verify-email",
                        json={"token": raw_token},
                    )

                    self.assertEqual(
                        replay_response.status_code,
                        400,
                    )

                    # TEST 8: Duplicate registration gives
                    # a generic response and sends no new email.
                    duplicate_response = client.post(
                        "/register",
                        json={
                            "full_name": "Integration Student",
                            "email": email,
                            "password": password,
                        },
                    )

                    self.assertEqual(
                        duplicate_response.status_code,
                        200,
                    )

                    self.assertEqual(
                        duplicate_response.json(),
                        register_response.json(),
                    )

                    fake_email.assert_called_once()


if __name__ == "__main__":
    unittest.main()
