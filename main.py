from fastapi import FastAPI, HTTPException, Depends
from db import SessionLocal, engine, Base
import services.service as user_service
from sqlalchemy.orm import Session
from schemas.schema import TransactionCreate, TransactionCreate, TransactionInDB, UserCreate,UserInDB,UserUpdate,WalletUpdate,WalletInDB,WalletCreate
from models.models import User, Wallet, Transaction
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
    
    if(db_wallet):
        transaction_data = TransactionCreate(
            user_id=user_id,
            wallet_id=db_wallet.id,
            transaction_type="CREDIT",
            amount=amount,
            description=description
        )
        # user_service.create_transaction(db, transaction_data)
        db_transaction = Transaction(**transaction_data.model_dump())
        db.add(db_transaction)
        db.commit()
        return {
            "user_id": user_id,
            "wallet_id": db_wallet.id,
            "transaction_type": "CREDIT",
            "amount": amount,
            "description": description
        }
    

@app.post("/wallet/{user_id}/withdraw-money")
def withdraw_money(user_id: int, amount: float, description: str, db: Session = Depends(get_db)):
    db_wallet = user_service.withdraw_money(db, user_id, amount, description)
    # Create transaction record
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if db_wallet:
        transaction_data = TransactionCreate(
            user_id=user_id,
            wallet_id=db_wallet.id,# type: ignore
            transaction_type="DEBIT",
            amount=amount,
            description=description
        )
        # user_service.create_transaction(db, transaction_data)
        db_transaction = Transaction(**transaction_data.model_dump())
        db.add(db_transaction)
        db.commit()
        return {
            "user_id": user_id,
            "wallet_id": db_wallet.id, #type: ignore
            "transaction_type": "DEBIT",
            "amount": amount,
            "description": description
        }
    

# ===============================================================================================

# Transaction endpoints
@app.get("/transactions/{user_id}", response_model=list[TransactionInDB])
def read_transactions(user_id: int, db: Session = Depends(get_db)):
    db_transactions = user_service.get_transactions(db, user_id)
    return db_transactions

@app.post("/transactions/", response_model=TransactionCreate)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = user_service.create_transaction(db, transaction)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not created")
    return {
        "id": db_transaction.id,
        "user_id": db_transaction.user_id,
        "wallet_id": db_transaction.wallet_id,
        "transaction_type": db_transaction.transaction_type,
        "amount": db_transaction.amount,
        "description": db_transaction.description,
        "reference_transaction_id": db_transaction.reference_transaction_id,
        "recipient_user_id": db_transaction.recipient_user_id,
        "created_at": db_transaction.created_at
    }