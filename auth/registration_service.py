
import re
import sqlite3

from auth.password import hash_password, validate_new_password
from auth.service import is_email_registered
from auth.user_repository import create_user

class DuplicateEmailError(ValueError):
    """Raised when an email address is already registered."""
    pass

def register_user(
    email: str,
    full_name: str,
    password: str,
) -> int:
    """Validate and create an unverified user account."""

    email = email.strip().lower()
    full_name = full_name.strip()

    if not email or not full_name:
        raise ValueError("Email and full name are required.")

    if len(full_name) > 100:
        raise ValueError("Full name is too long.")

    if len(email) > 254 or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email,
    ):
        raise ValueError("Enter a valid email address.")

    validate_new_password(password)

    if is_email_registered(email):
        raise DuplicateEmailError("Email is already registered.")

    password_hash = hash_password(password)

    try:
        return create_user(
            email=email,
            full_name=full_name,
            hashed_password=password_hash,
        )
    except sqlite3.IntegrityError:
        raise DuplicateEmailError(
            "Email is already registered."
        ) from None
