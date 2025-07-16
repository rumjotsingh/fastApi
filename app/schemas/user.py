from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "user"
class UserLogin(BaseModel):
    email:EmailStr
    password:str
class UserOut(BaseModel):
    email: EmailStr
    name: str
    role: str
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
class UserProfile(BaseModel):
    email: str
    name: str
    role: str

class TokenWithUser(BaseModel):
    access_token: str
    user: UserProfile

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
