from auth.registration_service import register_user
from auth.verification_service import issue_verification_token
from auth.verification_email_sender import (
    send_verification_email_for_token,
)

class RegistrationEmailDeliveryError(RuntimeError):
    """Verification email delivery could not be requested."""
    pass

def register_and_issue_verification(
    email: str,
    full_name: str,
    password: str,
) -> tuple[int, str]:
    """Register a user and issue an email verification token."""

    # Step 1: Validate and save the new account.
    user_id = register_user(
        email=email,
        full_name=full_name,
        password=password,
    )

    # Step 2: Create and save the verification ticket.
    raw_token = issue_verification_token(user_id)

    # Step 3: Return details to the email sender.
    return user_id, raw_token


def register_and_send_verification(
    email: str,
    full_name: str,
    password: str,
) -> int:
    """Register a user and send a verification email."""

    # Step 1: Register user and generate verification token.
    user_id, raw_token = register_and_issue_verification(
        email=email,
        full_name=full_name,
        password=password,
    )

    # Step 2: Send verification link to the user's email.
    try:
        send_verification_email_for_token(
            to_email=email.strip().lower(),
            raw_token=raw_token,
        )
    except Exception:
        raise RegistrationEmailDeliveryError(
            "Verification email delivery failed."
        ) from None

    # Step 3: Return only the user ID, not the secret token.
    return user_id