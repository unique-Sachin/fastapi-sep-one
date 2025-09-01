from pydantic import BaseModel, EmailStr
from models.models import Wallet,User
from schemas.schema import UserCreate, UserUpdate,WalletCreate



# create User
def create_user(db, user: UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# get User by ID
def get_user(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# get User by email
def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()

# get all Users
def get_all_users(db):
    return db.query(User).all()

# update User
def update_user(db, user_id: int, user: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user.model_dump().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# delete User
def delete_user(db, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# ----------------------------------------------------------------------------------------------------------------

# create Wallet
def create_wallet(db, wallet: WalletCreate):
    user_wallet = Wallet(**wallet.model_dump())
    db.add(user_wallet)
    db.commit()
    db.refresh(user_wallet)
    return user_wallet

# get wallet
def get_wallet(db, user_id: int):
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()

# add money to wallet
def add_money(db, user_id: int, amount: float, description: str):
    user_wallet = get_wallet(db, user_id)
    if user_wallet:
        user_wallet.balance = amount + float(user_wallet.balance)
        user_wallet.description = description
        db.commit()
        db.refresh(user_wallet)
    return user_wallet

# withdraw money from wallet
def withdraw_money(db, user_id: int, amount: float, description: str):
    user_wallet = get_wallet(db, user_id)
    if user_wallet:
        if(user_wallet.balance < amount):
            return {"error": "Insufficient balance"}
        user_wallet.balance = float(user_wallet.balance) - amount
        user_wallet.description = description
        db.commit()
        db.refresh(user_wallet)
    return user_wallet