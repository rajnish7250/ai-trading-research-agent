
from auth.email_service import send_email


def main():
    # Enter your own Resend account email.
    to_email = input(
        "Enter your Resend account email: "
    ).strip()

    if not to_email or "@" not in to_email:
        print("Please enter a valid email address.")
        return

    # Send a simple test message.
    email_id = send_email(
        to_email=to_email,
        subject="AI Trading Research Agent - Email Test",
        html_body="""
        <h2>Email Test Successful!</h2>
        <p>Hello!</p>
        <p>Your AI Trading Research Agent
        can send emails using Resend.</p>
        """,
    )

    print("Email request accepted by Resend!")
    print("Email ID:", email_id)


if __name__ == "__main__":
    main()
