from sqlalchemy.orm import Session
from models.token import Token
from models.user import User
from services.user_service import UserService
from datetime import datetime, timedelta
import secrets
import string

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = UserService.get_user_by_username(db, username)
        if not user:
            return False
        if not UserService.verify_password(password, user.hashed_password):
            return False
        return user
    
    @staticmethod
    def create_token(db: Session, user_id: int, expires_delta: timedelta = None):
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        # Generate a random token
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Create token record
        db_token = Token(
            token=token,
            user_id=user_id,
            expires_at=datetime.now() + expires_delta
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        
        return db_token
    
    @staticmethod
    def validate_token(db: Session, token: str):
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            return None
        
        # Check if token is expired
        if db_token.expires_at < datetime.now():
            return None
        
        return db_token
    
    @staticmethod
    def get_current_user(db: Session, token: str):
        db_token = AuthService.validate_token(db, token)
        if not db_token:
            return None
        
        user = UserService.get_user_by_id(db, db_token.user_id)
        return user
    
    @staticmethod
    def revoke_token(db: Session, token: str):
        db_token = db.query(Token).filter(Token.token == token).first()
        if db_token:
            db.delete(db_token)
            db.commit()
            return True
        return False