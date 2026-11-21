
from html import escape


VERIFICATION_EMAIL_SUBJECT = (
    "Verify your AI Trading Research Agent account"
)


def build_verification_email_html(
    verification_url: str,
) -> str:
    """Create the HTML content for a verification email."""

    # Safely insert the verification URL into HTML.
    safe_url = escape(verification_url, quote=True)

    return f"""
    <html>
      <body>
        <h2>Welcome to AI Trading Research Agent!</h2>

        <p>Thank you for registering.</p>

        <p>
          Please confirm your email address by
          clicking the button below.
        </p>

        <p>
          <a href="{safe_url}">
            Verify My Email
          </a>
        </p>

        <p>
          This verification link expires in 30 minutes.
        </p>

        <p>
          If you did not create this account,
          you can ignore this email.
        </p>
      </body>
    </html>
    """
