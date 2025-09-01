from fastapi import FastAPI, HTTPException, Depends
from db import SessionLocal, engine, Base
import services.service as user_service
from sqlalchemy.orm import Session
from schemas.schema import (
    TransactionCreate, TransactionInDB, UserCreate, UserInDB, UserUpdate, 
    WalletUpdate, WalletInDB, WalletCreate, TransferCreate, TransferResponse, 
    TransferInDB, ErrorResponse
)
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
    return db_transaction

# ===============================================================================================

# Transfer endpoints
@app.post("/transfer", response_model=TransferResponse, status_code=201)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db)):
    """Create a transfer between two users"""
    try:
        # Validate that sender and recipient exist
        sender = user_service.get_user(db, transfer.sender_user_id)
        recipient = user_service.get_user(db, transfer.recipient_user_id)
        
        if not sender:
            raise HTTPException(status_code=404, detail=f"Sender user {transfer.sender_user_id} not found")
        if not recipient:
            raise HTTPException(status_code=404, detail=f"Recipient user {transfer.recipient_user_id} not found")
        
        if transfer.sender_user_id == transfer.recipient_user_id:
            raise HTTPException(status_code=400, detail="Cannot transfer to yourself")
        
        if transfer.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        # Create the transfer
        result = user_service.create_transfer(db, transfer)
        
        # Check if it's an error response (insufficient balance)
        if "error" in result:
            raise HTTPException(
                status_code=400, 
                detail=result
            )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/transfer/{transfer_id}", response_model=TransferInDB)
def get_transfer(transfer_id: str, db: Session = Depends(get_db)):
    """Get transfer details by transfer ID"""
    db_transfer = user_service.get_transfer(db, transfer_id)
    if db_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return db_transfer