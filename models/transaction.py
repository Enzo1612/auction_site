from models import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Positive for deposits, negative for deductions
    balance = db.Column(db.Float, nullable=False)  # User's wallet balance after the transaction
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='transactions')

    def __repr__(self):
        return f'<Transaction {self.id} - User {self.user_id} - Amount {self.amount}>'