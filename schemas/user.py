from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    mobile_number: str
    age: Optional[int] = None
    address: Optional[str] = None
    full_name: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False  # Default to regular user

class UserOut(UserBase):
    id: int
    is_admin: bool = False  # Include is_admin in response

    class Config:
        from_attributes = True

        from pydantic import BaseModel

class PasswordUpdateForm(BaseModel):
    username: str
    password: str
    new_password: str