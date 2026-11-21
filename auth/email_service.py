
import os

import resend
from dotenv import load_dotenv


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
) -> str:
    """Send an email using Resend."""

    # Load environment variables from .env.
    load_dotenv()

    # Read our private API key and sender address.
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("RESEND_FROM_EMAIL")

    # Stop if email configuration is missing.
    if not api_key or not from_email:
        raise RuntimeError(
            "Resend email configuration is missing."
        )

    # Give the Resend SDK our API key.
    resend.api_key = api_key

    # Ask Resend to send the email.
    response = resend.Emails.send(
        {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
    )

    # Return Resend's email request ID.
    return response["id"]
