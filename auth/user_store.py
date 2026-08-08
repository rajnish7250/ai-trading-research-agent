from auth.password import hash_password

USER_STORE  = {
    "rajnish@gmail.com": {
        "email": "rajnish@gmail.com",
        "full_name": "Rajnish Kumar",
        "hashed_password": hash_password("Password123"),
        "disabled": False,
    }
}