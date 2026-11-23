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

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=12, max_length=72)


class AccountProfile(BaseModel):
    email: str
    full_name: str
    can_manage: bool


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=1, max_length=72)
