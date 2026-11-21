import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app, limiter


class ResendVerificationSecurityTest(unittest.TestCase):

    def setUp(self):
        """Start each test with fresh rate-limit counters."""
        limiter._storage.reset()

    @patch("main.request_verification_resend")
    def test_validation_privacy_and_rate_limit(
        self,
        fake_resend,
    ):
        client = TestClient(app)

        # TEST 1: Invalid requests must be rejected.
        invalid_requests = [
            {},
            {"email": ""},
            {"email": "x" * 255},
        ]

        for payload in invalid_requests:
            response = client.post(
                "/resend-verification",
                json=payload,
            )

            self.assertEqual(
                response.status_code,
                422,
            )

        # Invalid requests must not reach our service.
        fake_resend.assert_not_called()

        # TEST 2: Different accounts get the same reply.
        emails = [
            "unknown@example.com",
            "verified@example.com",
            "disabled@example.com",
            "student@example.com",
            "other@example.com",
        ]

        expected_message = (
            "If this email belongs to an eligible account, "
            "a verification email will be sent."
        )

        for email in emails:
            response = client.post(
                "/resend-verification",
                json={"email": email},
            )

            self.assertEqual(
                response.status_code,
                200,
            )

            self.assertEqual(
                response.json()["message"],
                expected_message,
            )

        self.assertEqual(
            fake_resend.call_count,
            5,
        )

        # TEST 3: Sixth request should be rate-limited.
        blocked_response = client.post(
            "/resend-verification",
            json={"email": "extra@example.com"},
        )

        self.assertEqual(
            blocked_response.status_code,
            429,
        )

        # Blocked request must not reach our service.
        self.assertEqual(
            fake_resend.call_count,
            5,
        )


if __name__ == "__main__":
    unittest.main()