from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import User
from models.transaction import Transaction
from models.wallet import Wallet
from models.token import Token
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db, username, email, password, first_name=None, last_name=None):
        hashed_password = pwd_context.hash(password)
        db_user = User(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        wallet = Wallet(user_id=db_user.id, balance=0.0)
        db.add(wallet)
        db.commit()

        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs):
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            for key, value in kwargs.items():
                setattr(db_user, key, value)
            db_user.updated_at = datetime.now()
            db.commit()
            db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_wallet_balance(db: Session, user_id: int, amount: float):
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db_user.wallet_balance += amount
            db_user.updated_at = datetime.now()
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def get_transaction_history(db: Session, user_id: int):
        """
        Retrieve the transaction history for a specific user.
        """
        return db.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)