from pydantic import BaseModel, EmailStr
from models.models import Transaction, Wallet, User, Transfer
from schemas.schema import TransactionCreate, TransactionInDB, UserCreate, UserUpdate, WalletCreate, TransferCreate
import uuid
from datetime import datetime



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


# ----------------------------------------------------------------------------------------------------------------

# get transactions
def get_transactions(db, user_id: int):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def create_transaction(db, transaction: TransactionCreate):
    try:
        # Create transaction without transfer_id initially for model_dump compatibility
        transaction_data = transaction.model_dump()
        db_transaction = Transaction(**transaction_data)
        db.add(db_transaction)
        db.commit()
        
        # Query fresh from database to avoid refresh issues
        created_transaction = db.query(Transaction).filter(Transaction.id == db_transaction.id).first()
        return created_transaction
        
    except Exception as e:
        db.rollback()
        raise e


# ----------------------------------------------------------------------------------------------------------------
# Transfer functions

def create_transfer(db, transfer: TransferCreate):
    """Create a transfer between two users"""
    try:
        # Generate unique transfer ID
        transfer_id = str(uuid.uuid4())
        
        # Get sender and recipient wallets
        sender_wallet = get_wallet(db, transfer.sender_user_id)
        recipient_wallet = get_wallet(db, transfer.recipient_user_id)
        
        if not sender_wallet:
            raise ValueError(f"Sender wallet not found for user {transfer.sender_user_id}")
        if not recipient_wallet:
            raise ValueError(f"Recipient wallet not found for user {transfer.recipient_user_id}")
        
        # Check if sender has sufficient balance
        if float(sender_wallet.balance) < transfer.amount:
            return {
                "error": "Insufficient balance",
                "current_balance": float(sender_wallet.balance),
                "required_amount": transfer.amount
            }
        
        # Create transfer record
        db_transfer = Transfer(
            id=transfer_id,
            sender_user_id=transfer.sender_user_id,
            recipient_user_id=transfer.recipient_user_id,
            amount=transfer.amount,
            description=transfer.description,
            status="completed"
        )
        db.add(db_transfer)
        db.flush()
        
        # Create sender transaction (debit)
        sender_transaction = TransactionCreate(
            user_id=transfer.sender_user_id,
            wallet_id=sender_wallet.id,
            transaction_type="TRANSFER_OUT",
            amount=transfer.amount,
            description=f"Transfer to user {transfer.recipient_user_id}: {transfer.description}",
            transfer_id=transfer_id
        )
        
        db_sender_transaction = Transaction(**sender_transaction.model_dump())
        db.add(db_sender_transaction)
        db.flush()
        
        # Create recipient transaction (credit)
        recipient_transaction = TransactionCreate(
            user_id=transfer.recipient_user_id,
            wallet_id=recipient_wallet.id,
            transaction_type="TRANSFER_IN",
            amount=transfer.amount,
            description=f"Transfer from user {transfer.sender_user_id}: {transfer.description}",
            transfer_id=transfer_id
        )
        
        db_recipient_transaction = Transaction(**recipient_transaction.model_dump())
        db.add(db_recipient_transaction)
        db.flush()
        
        # Update wallet balances
        sender_wallet.balance = float(sender_wallet.balance) - transfer.amount
        recipient_wallet.balance = float(recipient_wallet.balance) + transfer.amount
        
        # Update transfer with transaction IDs
        db_transfer.sender_transaction_id = db_sender_transaction.id
        db_transfer.recipient_transaction_id = db_recipient_transaction.id
        
        # Commit all changes
        db.commit()
        
        return {
            "transfer_id": transfer_id,
            "sender_transaction_id": db_sender_transaction.id,
            "recipient_transaction_id": db_recipient_transaction.id,
            "amount": transfer.amount,
            "sender_new_balance": float(sender_wallet.balance),
            "recipient_new_balance": float(recipient_wallet.balance),
            "status": "completed"
        }
        
    except Exception as e:
        db.rollback()
        raise e


def get_transfer(db, transfer_id: str):
    """Get transfer details by transfer ID"""
    return db.query(Transfer).filter(Transfer.id == transfer_id).first()