import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from auth.registration_service import DuplicateEmailError
from auth.registration_flow import RegistrationEmailDeliveryError


GENERIC_MESSAGE = (
    "If this email is eligible for registration, "
    "a verification email will be sent."
)

VALID_PAYLOAD = {
    "full_name": "Test Student",
    "email": "student@example.com",
    "password": "StrongPassword123!",
}


class RegistrationAPITest(unittest.TestCase):

    @patch("main.register_and_send_verification")
    def test_success(self, fake_register):
        client = TestClient(app)

        response = client.post(
            "/register",
            json=VALID_PAYLOAD,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": GENERIC_MESSAGE},
        )

        fake_register.assert_called_once_with(
            email="student@example.com",
            full_name="Test Student",
            password="StrongPassword123!",
        )

    @patch(
        "main.register_and_send_verification",
        side_effect=DuplicateEmailError(
            "Email is already registered."
        ),
    )
    def test_duplicate_email_is_private(self, fake_register):
        client = TestClient(app)

        response = client.post(
            "/register",
            json=VALID_PAYLOAD,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": GENERIC_MESSAGE},
        )

    @patch(
        "main.register_and_send_verification",
        side_effect=ValueError("Invalid password."),
    )
    def test_invalid_details(self, fake_register):
        client = TestClient(app)

        response = client.post(
            "/register",
            json=VALID_PAYLOAD,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Invalid registration details.",
        )

    @patch(
        "main.register_and_send_verification",
        side_effect=RegistrationEmailDeliveryError(
            "Provider failed."
        ),
    )
    def test_email_provider_failure(self, fake_register):
        client = TestClient(app)

        response = client.post(
            "/register",
            json=VALID_PAYLOAD,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": GENERIC_MESSAGE},
        )


if __name__ == "__main__":
    unittest.main()