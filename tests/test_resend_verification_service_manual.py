import unittest
from unittest.mock import patch

from auth.resend_verification_service import (
    request_verification_resend,
)


class ResendVerificationServiceTest(unittest.TestCase):

    @patch(
        "auth.resend_verification_service."
        "send_verification_email_for_token"
    )
    @patch(
        "auth.resend_verification_service."
        "save_verification_token_with_cooldown",
        return_value=True,
    )
    @patch(
        "auth.resend_verification_service."
        "generate_verification_token",
        return_value=(
            "FAKE_TOKEN",
            "FAKE_HASH",
            "2099-01-01T00:00:00+00:00",
        ),
    )
    @patch(
        "auth.resend_verification_service."
        "get_user_by_email",
        return_value={
            "id": 123,
            "email": "student@example.com",
            "is_verified": False,
            "disabled": False,
        },
    )
    def test_eligible_user_receives_email(
        self,
        fake_lookup,
        fake_token,
        fake_save,
        fake_send,
    ):

        # Step 1: Request another verification email.
        result = request_verification_resend(
            "student@example.com"
        )

        # Step 2: The public-facing service returns no details.
        self.assertIsNone(result)

        # Step 3: Check the user lookup.
        fake_lookup.assert_called_once_with(
            "student@example.com"
        )

        # Step 4: Check token generation.
        fake_token.assert_called_once()

        # Step 5: Check the cooldown function.
        fake_save.assert_called_once_with(
            user_id=123,
            token_hash="FAKE_HASH",
            expires_at="2099-01-01T00:00:00+00:00",
        )

        # Step 6: Check email delivery was requested.
        fake_send.assert_called_once_with(
            to_email="student@example.com",
            raw_token="FAKE_TOKEN",
        )
    @patch(
        "auth.resend_verification_service."
        "send_verification_email_for_token"
    )
    @patch(
        "auth.resend_verification_service."
        "generate_verification_token"
    )
    @patch(
        "auth.resend_verification_service."
        "get_user_by_email"
    )
    def test_ineligible_users_do_not_receive_email(
        self,
        fake_lookup,
        fake_token,
        fake_send,
    ):

        # Three situations where email must not be sent.
        test_cases = [
            ("unknown", None),
            (
                "verified",
                {
                    "id": 1,
                    "email": "verified@example.com",
                    "is_verified": True,
                    "disabled": False,
                },
            ),
            (
                "disabled",
                {
                    "id": 2,
                    "email": "disabled@example.com",
                    "is_verified": False,
                    "disabled": True,
                },
            ),
        ]

        for case_name, user in test_cases:
            with self.subTest(case=case_name):

                # Pretend the database returned this user.
                fake_lookup.return_value = user

                # Run the resend service.
                result = request_verification_resend(
                    "student@example.com"
                )

                # No account details should be returned.
                self.assertIsNone(result)

                # No verification token should be generated.
                fake_token.assert_not_called()

                # No email should be sent.
                fake_send.assert_not_called()
    @patch(
        "auth.resend_verification_service."
        "send_verification_email_for_token"
    )
    @patch(
        "auth.resend_verification_service."
        "save_verification_token_with_cooldown",
        return_value=False,
    )
    @patch(
        "auth.resend_verification_service."
        "generate_verification_token",
        return_value=(
            "FAKE_TOKEN",
            "FAKE_HASH",
            "2099-01-01T00:00:00+00:00",
        ),
    )
    @patch(
        "auth.resend_verification_service."
        "get_user_by_email",
        return_value={
            "id": 123,
            "email": "student@example.com",
            "is_verified": False,
            "disabled": False,
        },
    )
    def test_cooldown_prevents_email(
        self,
        fake_lookup,
        fake_token,
        fake_save,
        fake_send,
    ):

        # Step 1: Request another verification email.
        result = request_verification_resend(
            "student@example.com"
        )

        # Step 2: Check that no details are returned.
        self.assertIsNone(result)

        # Step 3: User lookup should happen.
        fake_lookup.assert_called_once()

        # Step 4: Token generation was attempted.
        fake_token.assert_called_once()

        # Step 5: Cooldown check should happen.
        fake_save.assert_called_once()

        # Step 6: Email must NOT be sent.
        fake_send.assert_not_called()
    @patch(
        "auth.resend_verification_service."
        "send_verification_email_for_token",
        side_effect=RuntimeError("SIMULATED_PROVIDER_FAILURE"),
    )
    @patch(
        "auth.resend_verification_service."
        "save_verification_token_with_cooldown",
        return_value=True,
    )
    @patch(
        "auth.resend_verification_service."
        "generate_verification_token",
        return_value=(
            "FAKE_SECRET_TOKEN",
            "FAKE_HASH",
            "2099-01-01T00:00:00+00:00",
        ),
    )
    @patch(
        "auth.resend_verification_service."
        "get_user_by_email",
        return_value={
            "id": 123,
            "email": "student@example.com",
            "is_verified": False,
            "disabled": False,
        },
    )
    def test_email_delivery_failure(
        self,
        fake_lookup,
        fake_token,
        fake_save,
        fake_send,
    ):

        # Step 1: Run the resend request while
        # the fake email provider is failing.
        with self.assertLogs(
            "auth.resend_verification_service",
            level="ERROR",
        ) as captured_logs:

            result = request_verification_resend(
                "student@example.com"
            )

        # Step 2: The service should handle the error.
        self.assertIsNone(result)

        # Step 3: Check that the expected functions ran.
        fake_lookup.assert_called_once()
        fake_token.assert_called_once()
        fake_save.assert_called_once()
        fake_send.assert_called_once_with(
            to_email="student@example.com",
            raw_token="FAKE_SECRET_TOKEN",
        )

        # Step 4: Check that a failure was logged.
        log_text = "\n".join(captured_logs.output)

        self.assertIn(
            "Verification email delivery failed.",
            log_text,
        )

        # Step 5: Make sure secrets are NOT logged.
        self.assertNotIn(
            "FAKE_SECRET_TOKEN",
            log_text,
        )

        self.assertNotIn(
            "student@example.com",
            log_text,
        )

        self.assertNotIn(
            "SIMULATED_PROVIDER_FAILURE",
            log_text,
        )

if __name__ == "__main__":
    unittest.main()