
import unittest
from unittest.mock import patch, Mock

from auth_ui import (
    validate_registration,
    register_account,
    verify_account,
    resend_verification,
)


class AuthUITests(unittest.TestCase):

    def test_valid_registration(self):
        self.assertIsNone(
            validate_registration(
                "Test User",
                "test@example.com",
                "SecurePassword123!",
                "SecurePassword123!",
            )
        )

    def test_password_mismatch(self):
        self.assertIsNotNone(
            validate_registration(
                "Test User",
                "test@example.com",
                "SecurePassword123!",
                "DifferentPassword123!",
            )
        )

    def test_short_password(self):
        self.assertIsNotNone(
            validate_registration(
                "Test User",
                "test@example.com",
                "short",
                "short",
            )
        )

    def test_password_byte_limit(self):
        password = "é" * 37
        self.assertIsNotNone(
            validate_registration(
                "Test User",
                "test@example.com",
                password,
                password,
            )
        )

    @patch("auth_ui.requests.post")
    def test_registration_request(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"message": "Request accepted"},
        )

        result = register_account(
            "http://127.0.0.1:8000",
            "Test User",
            "TEST@example.com",
            "SecurePassword123!",
        )

        self.assertEqual(result, "Request accepted")
        self.assertEqual(
            mock_post.call_args.kwargs["json"]["email"],
            "test@example.com",
        )

    @patch("auth_ui.requests.post")
    def test_verification_request(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"message": "Verified"},
        )

        result = verify_account(
            "http://127.0.0.1:8000",
            "test-token",
        )

        self.assertEqual(result, "Verified")
        self.assertEqual(
            mock_post.call_args.kwargs["json"],
            {"token": "test-token"},
        )

    @patch("auth_ui.requests.post")
    def test_resend_request(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"message": "Request accepted"},
        )

        result = resend_verification(
            "http://127.0.0.1:8000",
            "TEST@example.com",
        )

        self.assertEqual(result, "Request accepted")
        self.assertEqual(
            mock_post.call_args.kwargs["json"],
            {"email": "test@example.com"},
        )


if __name__ == "__main__":
    unittest.main()
