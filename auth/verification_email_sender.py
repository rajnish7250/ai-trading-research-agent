from auth.email_service import send_email
from auth.verification_email import (
    VERIFICATION_EMAIL_SUBJECT,
    build_verification_email_html,
)
from auth.verification_link import build_verification_url


def send_verification_email(
    to_email: str,
    verification_url: str,
) -> str:
    """Send an account verification email using Resend."""

    # Step 1: Prepare the email content.
    html_body = build_verification_email_html(
        verification_url
    )

    # Step 2: Send the email through Resend.
    email_id = send_email(
        to_email=to_email,
        subject=VERIFICATION_EMAIL_SUBJECT,
        html_body=html_body,
    )

    # Step 3: Return Resend's email ID.
    return email_id


def send_verification_email_for_token(
    to_email: str,
    raw_token: str,
) -> str:
    """Build a verification link and send the email."""

    # Step 1: Build the Streamlit verification URL.
    verification_url = build_verification_url(raw_token)

    # Step 2: Send the verification email.
    return send_verification_email(
        to_email=to_email,
        verification_url=verification_url,
    )