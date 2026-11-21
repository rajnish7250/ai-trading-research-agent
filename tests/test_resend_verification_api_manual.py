import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


class ResendVerificationAPITest(unittest.TestCase):

    @patch("main.request_verification_resend")
    def test_resend_endpoint_success(self, fake_resend):

        # Create a local API test client.
        client = TestClient(app)

        # Send a fake resend request.
        response = client.post(
            "/resend-verification",
            json={
                "email": "student@example.com"
            },
        )

        # Check HTTP status.
        self.assertEqual(
            response.status_code,
            200,
        )

        # Check the safe response message.
        self.assertEqual(
            response.json(),
            {
                "message": (
                    "If this email belongs to an eligible account, "
                    "a verification email will be sent."
                )
            },
        )

        # Check that FastAPI called our service.
        fake_resend.assert_called_once_with(
            "student@example.com"
        )


if __name__ == "__main__":
    unittest.main()