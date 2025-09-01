from pydantic import BaseModel, EmailStr
from typing import Optional,List
import datetime

# create User schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone_number: Optional[str]
    balance: Optional[float]

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str]

class UserInDB(UserBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

