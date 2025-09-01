from fastapi import FastAPI, HTTPException, Depends
from db import SessionLocal, engine, Base
import services.service as user_service
from sqlalchemy.orm import Session
from schemas.schema import UserCreate,UserInDB,UserUpdate,WalletUpdate,WalletInDB,WalletCreate

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

# ===============================================================================================
# User endpoints
@app.post("/users/", response_model=UserInDB)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.create_user(db, user)
    if db_user:
        # create wallet
        wallet_data = WalletCreate(user_id=db_user.id, balance=db_user.balance, description="Initial Wallet") # type: ignore
        user_service.create_wallet(db, wallet_data)
    return db_user

@app.get("/users/{user_id}", response_model=UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=list[UserInDB])
def read_users(db: Session = Depends(get_db)):
    db_users = user_service.get_all_users(db)
    return db_users

@app.put("/users/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", response_model=UserInDB)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ===============================================================================================

# Wallet endpoints
@app.get("/wallet/{user_id}/balance")
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    db_wallet = user_service.get_wallet(db, user_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"user_id": user_id, "balance": db_wallet.balance}

@app.post("/wallet/{user_id}/add-money")
def add_money(user_id: int, amount: float, description: str, db: Session = Depends(get_db)):
    db_wallet = user_service.add_money(db, user_id, amount, description)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet

@app.post("/wallet/{user_id}/withdraw-money")
def withdraw_money(user_id: int, amount: float, description: str, db: Session = Depends(get_db)):
    db_wallet = user_service.withdraw_money(db, user_id, amount, description)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet

# ===============================================================================================

# 