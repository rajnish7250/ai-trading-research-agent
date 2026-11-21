import os

from dotenv import load_dotenv
from urllib.parse import urlencode, urlsplit, urlunsplit


def build_verification_url(raw_token: str) -> str:
    """Build the public Streamlit email verification link."""

    load_dotenv()

    public_url = os.getenv("PUBLIC_APP_URL", "").strip()

    if not public_url:
        raise RuntimeError("PUBLIC_APP_URL is not configured.")

    if not raw_token:
        raise ValueError("Verification token is required.")

    parts = urlsplit(public_url)

    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("PUBLIC_APP_URL is invalid.")

    if parts.query or parts.fragment:
        raise ValueError(
            "PUBLIC_APP_URL must not contain query parameters or fragments."
        )

    if parts.scheme != "https" and parts.hostname not in (
        "localhost",
        "127.0.0.1",
    ):
        raise ValueError(
            "HTTPS is required for non-local verification links."
        )

    query = urlencode({"verify_token": raw_token})

    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path or "/",
        query,
        "",
    ))