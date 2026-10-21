import os
from auth.password import hash_password

def _build_user(email_env: str, password_env: str, full_name: str):
    email = os.getenv(email_env, "").strip().lower()
    password = os.getenv(password_env, "")

    if not email and not password:
        return None

    if not email or not password:
        raise ValueError(
            f"Both {email_env} and {password_env} must be configured."
        )

    return {
        "email": email,
        "full_name": full_name,
        "hashed_password": hash_password(password),
        "disabled": False,
    }


USER_STORE = {}

for email_env, password_env, full_name in [
    ("DEMO_USER_EMAIL", "DEMO_USER_PASSWORD", "Demo User 1"),
    ("DEMO_USER2_EMAIL", "DEMO_USER2_PASSWORD", "Demo User 2"),
]:
    user = _build_user(email_env, password_env, full_name)

    if user:
        if user["email"] in USER_STORE:
            raise ValueError("Duplicate configured user email.")

        USER_STORE[user["email"]] = user
