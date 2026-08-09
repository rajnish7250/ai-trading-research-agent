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

    if email is None:
        raise credentials_exception

    user = get_user(email)

    if user is None:
        raise credentials_exception

    return user