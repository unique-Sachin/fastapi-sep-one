from fastapi import FastAPI, HTTPException, Depends
from db import SessionLocal, engine, Base
from services import user_service
from sqlalchemy.orm import Session
from models import UserModel
from schemas import user_schema

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the database tables
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/users/", response_model=user_schema.UserInDB)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.create_user(db, user)
    return db_user

@app.get("/users/{user_id}", response_model=user_schema.UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=list[user_schema.UserInDB])
def read_users(db: Session = Depends(get_db)):
    db_users = user_service.get_all_users(db)
    return db_users

@app.put("/users/{user_id}", response_model=user_schema.UserInDB)
def update_user(user_id: int, user: user_schema.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
