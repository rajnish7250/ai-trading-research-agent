
import hashlib

from auth.token_service import generate_verification_token
from auth.token_repository import (
    save_auth_token,
    redeem_verification_token,
)


def issue_verification_token(user_id: int) -> str:
    """Create and save a verification ticket."""

    raw_token, token_hash, expires_at = (
        generate_verification_token()
    )

    save_auth_token(
        user_id=user_id,
        token_hash=token_hash,
        purpose="email_verification",
        expires_at=expires_at,
    )

    # Return the secret only so the email sender can deliver it.
    return raw_token


def verify_email_token(raw_token: str) -> bool:
    """Redeem a verification ticket supplied by a user."""

    if not isinstance(raw_token, str):
        return False

    if not raw_token or len(raw_token) > 256:
        return False

    # Convert the secret ticket into its fingerprint.
    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    # Activate the user and mark the ticket as used.
    return redeem_verification_token(token_hash)
