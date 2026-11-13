from pydantic import BaseModel
from typing import Literal

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    username: str
    password: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdminPanel(BaseModel):
    role: str = Literal["Voter", "polling_officer", "admin"]