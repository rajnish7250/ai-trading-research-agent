import unittest
from unittest.mock import patch

from auth.verification_email_sender import (
    send_verification_email_for_token,
)


class VerificationEmailSenderTest(unittest.TestCase):

    @patch(
        "auth.verification_email_sender.send_email",
        return_value="fake-email-id",
    )
    def test_verification_email(self, fake_send):

        # Step 1: Use a local test website address.
        with patch.dict(
            "os.environ",
            {"PUBLIC_APP_URL": "http://127.0.0.1:8501"},
        ):

            # Step 2: Call our email helper.
            email_id = send_verification_email_for_token(
                to_email="test@example.com",
                raw_token="TEST_TOKEN_ONLY",
            )

        # Step 3: Check the fake email ID.
        self.assertEqual(email_id, "fake-email-id")

        # Step 4: Check that the email function was called.
        fake_send.assert_called_once()

        # Step 5: Check the recipient.
        email_data = fake_send.call_args.kwargs

        self.assertEqual(
            email_data["to_email"],
            "test@example.com",
        )

        # Step 6: Check the verification link.
        self.assertIn(
            "http://127.0.0.1:8501/?verify_token=TEST_TOKEN_ONLY",
            email_data["html_body"],
        )


if __name__ == "__main__":
    unittest.main()