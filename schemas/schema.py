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

class TransactionCreate(TransactionBase):
    transfer_id: Optional[str] = None

class TransactionUpdate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    id: int

    class Config:
        orm_mode = True


# Transfer schemas
class TransferBase(BaseModel):
    sender_user_id: int
    recipient_user_id: int
    amount: float
    description: str

class TransferCreate(TransferBase):
    pass

class TransferResponse(BaseModel):
    transfer_id: str
    sender_transaction_id: int
    recipient_transaction_id: int
    amount: float
    sender_new_balance: float
    recipient_new_balance: float
    status: str

class TransferInDB(TransferBase):
    id: str
    status: str
    sender_transaction_id: Optional[int]
    recipient_transaction_id: Optional[int]
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class ErrorResponse(BaseModel):
    error: str
    current_balance: float
    required_amount: float
