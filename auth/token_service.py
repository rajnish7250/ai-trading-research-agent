
import hashlib
import secrets
from datetime import datetime, timedelta, timezone


VERIFICATION_TOKEN_MINUTES = 30


def generate_verification_token() -> tuple[str, str, str]:
    return generate_auth_token(VERIFICATION_TOKEN_MINUTES)


def generate_auth_token(minutes: int) -> tuple[str, str, str]:
    """Generate an expiring token and its database fingerprint."""

    # Generate a cryptographically secure random token.
    raw_token = secrets.token_urlsafe(32)

    # Store only this fingerprint in the database.
    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=minutes)
    ).isoformat()

    return raw_token, token_hash, expires_at


def is_verification_token_valid(token_record: dict | None) -> bool:
    """Check whether a saved verification ticket is usable."""

    # Ticket does not exist.
    if token_record is None:
        return False

    # Ticket must be for email verification.
    if token_record["purpose"] != "email_verification":
        return False

    # Ticket must not have been used already.
    if token_record["used_at"] is not None:
        return False

    # Ticket must not have expired.
    expires_at = datetime.fromisoformat(
        token_record["expires_at"]
    )

    if expires_at <= datetime.now(timezone.utc):
        return False

    return True
