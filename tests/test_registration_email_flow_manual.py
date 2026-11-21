import unittest
from unittest.mock import patch

from auth.registration_flow import (
    register_and_send_verification,
)


class RegistrationEmailFlowTest(unittest.TestCase):

    @patch(
        "auth.registration_flow.send_verification_email_for_token"
    )
    @patch(
        "auth.registration_flow.register_and_issue_verification",
        return_value=(123, "FAKE_TOKEN_ONLY"),
    )
    def test_registration_sends_verification_email(
        self,
        fake_register,
        fake_send_email,
    ):

        # Step 1: Run our registration flow.
        user_id = register_and_send_verification(
            email=" Student@Example.com ",
            full_name="Test Student",
            password="FakePassword123!",
        )

        # Step 2: Check the returned user ID.
        self.assertEqual(user_id, 123)

        # Step 3: Check registration was requested.
        fake_register.assert_called_once_with(
            email=" Student@Example.com ",
            full_name="Test Student",
            password="FakePassword123!",
        )

        # Step 4: Check the correct email and token.
        fake_send_email.assert_called_once_with(
            to_email="student@example.com",
            raw_token="FAKE_TOKEN_ONLY",
        )


if __name__ == "__main__":
    unittest.main()