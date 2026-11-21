import logging

from auth.user_repository import get_user_by_email
from auth.token_service import generate_verification_token
from auth.token_repository import (
    save_verification_token_with_cooldown,
)
from auth.verification_email_sender import (
    send_verification_email_for_token,
)


logger = logging.getLogger(__name__)


def request_verification_resend(email: str) -> None:
    """Request another verification email for an eligible account."""

    # Step 1: Reject invalid input.
    if not isinstance(email, str):
        return

    # Step 2: Find the registered user.
    user = get_user_by_email(email)

    # Step 3: Do nothing if the account is not eligible.
    if user is None:
        return

    if user["is_verified"] or user["disabled"]:
        return

    # Step 4: Generate a fresh verification ticket.
    raw_token, token_hash, expires_at = (
        generate_verification_token()
    )

    # Step 5: Save the ticket only if cooldown allows it.
    allowed = save_verification_token_with_cooldown(
        user_id=user["id"],
        token_hash=token_hash,
        expires_at=expires_at,
    )

    if not allowed:
        return

    # Step 6: Send the verification email.
    try:
        send_verification_email_for_token(
            to_email=user["email"],
            raw_token=raw_token,
        )

    except Exception:
        # Never log the email address or secret token.
        logger.error(
            "Verification email delivery failed. "
            "Retry is possible after the cooldown."
        )