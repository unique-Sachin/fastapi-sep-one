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


class WalletBase(BaseModel):
    user_id: int
    balance: float

class WalletCreate(WalletBase):
    description: str

class WalletUpdate(WalletBase):
    description: Optional[str]

class WalletInDB(WalletBase):
    id: int

    class Config:
        orm_mode = True

# creating transaction schema

class TransactionBase(BaseModel):
    user_id: int
    wallet_id: int
    transaction_type: str
    amount: float
    description: str
    reference_transaction_id: Optional[int]
    recipient_user_id: Optional[int]
    created_at: datetime.datetime

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    id: int

    class Config:
        orm_mode = True
