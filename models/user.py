from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from models import db
from werkzeug.security import check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):  # Inherit from UserMixin
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Wallet
    wallet = db.relationship(
        'Wallet',
        back_populates='user',
        cascade="all, delete-orphan",  # Cascade delete to remove wallet when user is deleted
        uselist=False
    )

    bids = db.relationship('Bid', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    # Relationship with Transactions
    transactions = db.relationship(
        'Transaction',
        back_populates='user',
        cascade="all, delete-orphan",  # Cascade delete to remove transactions when user is deleted
        lazy=True
    )

    def check_password(self, password):
        # If the password doesn't have a method (like the admin password created with a script)
        if self.hashed_password and not self.hashed_password.startswith('pbkdf2:sha256:'):
            # Use bcrypt to verify password
            from flask_bcrypt import Bcrypt
            from flask import current_app
            bcrypt = Bcrypt(current_app)
            return bcrypt.check_password_hash(self.hashed_password, password)
        else:
            # Use Werkzeug to verify password
            return check_password_hash(self.hashed_password, password)

    def get_id(self):
        """Return the user ID as a string (required by Flask-Login)."""
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username} (ID: {self.id})>"
    
