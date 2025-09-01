from sqlalchemy import TIMESTAMP, Integer, Numeric, String, Column, ForeignKey, func
from sqlalchemy.orm import relationship

from db import Base

# creating user models

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(15))
    balance = Column(Numeric(10, 2), default=0.00)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    wallet = relationship("Wallet", back_populates="user")


# creating wallet models
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Numeric(10, 2), default=0.00)
    description = Column(String(255))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="wallet")


# creating transaction model
# // Transactions Collection
# {
#   "_id": ObjectId,
#   "user_id": ObjectId,
#   "transaction_type": "CREDIT|DEBIT|TRANSFER_IN|TRANSFER_OUT",
#   "amount": 0.00,
#   "description": "string",
#   "reference_transaction_id": ObjectId, // For linking transfers
#   "recipient_user_id": ObjectId, // For transfers
#   "created_at": Date
# }

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255))
    reference_transaction_id = Column(Integer, ForeignKey("transactions.id"))
    recipient_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")