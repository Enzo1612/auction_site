from datetime import datetime
from models import db

class Token(db.Model):
    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Fixed table name
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'purchase', 'bid', 'refund', etc.
    transaction_id = db.Column(db.Integer, nullable=True)  # Foreign key to purchase, bid, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='token_transactions')

    def __repr__(self):
        return f'<Token Transaction {self.id}: {self.amount} tokens for User {self.user_id}>'