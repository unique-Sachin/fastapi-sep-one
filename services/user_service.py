from pydantic import BaseModel, EmailStr
from models.UserModel import User
from schemas.user_schema import UserCreate, UserUpdate



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