
from auth.user_store import USER_STORE
from auth.user_repository import get_user_by_email
from auth.password import verify_password


def get_user(email: str):
    """Find a demo user or a registered SQLite user."""

    if not isinstance(email, str):
        return None

    normalized_email = email.strip().lower()

    if not normalized_email:
        return None

    # First, protect our existing demo accounts.
    demo_user = USER_STORE.get(normalized_email)

    if demo_user is not None:
        return demo_user

    # Otherwise, search registered users in SQLite.
    return get_user_by_email(normalized_email)


def authenticate_user(email: str, password: str):
    """Check the user's password and account status."""

    user = get_user(email)

    if user is None:
        return None

    if user.get("disabled", False):
        return None

    if user.get("is_verified", True) is False:
        return None

    if not verify_password(
        password,
        user["hashed_password"],
    ):
        return None

    return user


def is_email_registered(email: str) -> bool:
    """Check whether an email belongs to any existing account."""

    if not isinstance(email, str):
        return False

    normalized_email = email.strip().lower()

    if not normalized_email:
        return False

    # Check our existing demo accounts first.
    if normalized_email in USER_STORE:
        return True

    # Then check registered users in SQLite.
    return get_user_by_email(normalized_email) is not None
