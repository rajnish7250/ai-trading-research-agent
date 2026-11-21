from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    message: str


class ResendVerificationRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)


class ResendVerificationResponse(BaseModel):
    message: str