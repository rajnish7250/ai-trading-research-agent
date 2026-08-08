from auth.user_store import USER_STORE
from auth.password import verify_password
def get_user(email: str):
    return USER_STORE.get(email)

def authenticate_user(email: str, password: str):
    user = get_user(email)
    
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user