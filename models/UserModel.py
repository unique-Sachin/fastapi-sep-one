from sqlalchemy import TIMESTAMP, Integer, Numeric, String, Column, ForeignKey, func
from sqlalchemy.orm import relationship

from db import Base

# create the User model

# id SERIAL PRIMARY KEY,
#     username VARCHAR(50) UNIQUE NOT NULL,
#     email VARCHAR(100) UNIQUE NOT NULL,
#     password VARCHAR(255) NOT NULL,
#     phone_number VARCHAR(15),
#     balance DECIMAL(10,2) DEFAULT 0.00,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

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
