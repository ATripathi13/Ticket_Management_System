from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.user

class UserResponse(UserBase):
    id: int
    role: UserRole

    model_config = {
        "from_attributes": True
    }
