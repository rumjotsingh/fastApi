from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserInDB(BaseModel):
    id: Optional[str] = Field(alias="_id")
    email: EmailStr
    hashed_password: str
    name: str
    role: str = "user"
