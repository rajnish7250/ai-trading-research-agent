from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def validate_new_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < 12:
        raise ValueError(
            "Password must contain at least 12 characters."
        )

    if len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Password is too long for the current password system."
        )
