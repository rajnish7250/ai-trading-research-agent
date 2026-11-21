
from datetime import datetime, timedelta, timezone

from auth.token_service import is_verification_token_valid


def main():
    now = datetime.now(timezone.utc)

    # 1. Genuine ticket that expires in 30 minutes.
    valid_ticket = {
        "purpose": "email_verification",
        "used_at": None,
        "expires_at": (
            now + timedelta(minutes=30)
        ).isoformat(),
    }

    assert is_verification_token_valid(valid_ticket)
    print("Valid ticket accepted: PASSED")

    # 2. Ticket that expired 5 minutes ago.
    expired_ticket = {
        **valid_ticket,
        "expires_at": (
            now - timedelta(minutes=5)
        ).isoformat(),
    }

    assert not is_verification_token_valid(expired_ticket)
    print("Expired ticket rejected: PASSED")

    # 3. Ticket that was already used.
    used_ticket = {
        **valid_ticket,
        "used_at": now.isoformat(),
    }

    assert not is_verification_token_valid(used_ticket)
    print("Used ticket rejected: PASSED")

    # 4. Ticket meant for resetting a password.
    wrong_purpose_ticket = {
        **valid_ticket,
        "purpose": "password_reset",
    }

    assert not is_verification_token_valid(wrong_purpose_ticket)
    print("Wrong-purpose ticket rejected: PASSED")

    # 5. Ticket not found.
    assert not is_verification_token_valid(None)
    print("Missing ticket rejected: PASSED")


if __name__ == "__main__":
    main()
