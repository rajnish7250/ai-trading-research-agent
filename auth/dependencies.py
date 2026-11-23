
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from auth.jwt_handler import verify_access_token
from auth.service import get_user

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login",
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = verify_access_token(token)
    except JWTError:
        raise credentials_exception

    email = payload.get("sub")

    if not isinstance(email, str) or not email:
        raise credentials_exception

    user = get_user(email)

    return require_active_session(user, payload.get("uid"), payload.get("sv"))


def require_active_session(user: dict | None, user_id, session_version) -> dict:
    if (
        user is None
        or user.get("disabled", False)
        or user.get("is_verified", True) is False
        or (user.get("id"), user.get("session_version")) != (user_id, session_version)
    ):
        raise credentials_exception

    return user


def ensure_account_session(user: dict) -> None:
    """Recheck the session after acquiring the research lock."""
    require_active_session(
        get_user(user["email"]), user.get("id"), user.get("session_version"),
    )
