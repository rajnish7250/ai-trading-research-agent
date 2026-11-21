
"""Frontend helpers for registration and email verification."""

import re

import requests


AUTH_TIMEOUT = 15


def validate_registration(full_name, email, password, confirm_password):
    """Check form values before sending them to FastAPI."""
    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name or len(full_name) > 100:
        return "Full name must contain 1 to 100 characters."

    if len(email) > 254 or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email
    ):
        return "Enter a valid email address."

    if len(password) < 12:
        return "Password must contain at least 12 characters."

    if len(password.encode("utf-8")) > 72:
        return "Password is too long (maximum 72 UTF-8 bytes)."

    if password != confirm_password:
        return "Passwords do not match."

    return None


def register_account(api_base_url, full_name, email, password):
    """Ask FastAPI to register an account."""
    response = requests.post(
        f"{api_base_url}/register",
        json={
            "full_name": full_name.strip(),
            "email": email.strip().lower(),
            "password": password,
        },
        timeout=AUTH_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["message"]


def verify_account(api_base_url, token):
    """Send the one-time verification token to FastAPI."""
    response = requests.post(
        f"{api_base_url}/verify-email",
        json={"token": token},
        timeout=AUTH_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["message"]


def resend_verification(api_base_url, email):
    """Request another verification email."""
    response = requests.post(
        f"{api_base_url}/resend-verification",
        json={"email": email.strip().lower()},
        timeout=AUTH_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["message"]
