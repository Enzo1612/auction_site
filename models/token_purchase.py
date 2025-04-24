from models import db
from datetime import datetime

class TokenPurchase(db.Model):
    __tablename__ = "token_purchases"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_pack_id = db.Column(db.Integer, db.ForeignKey('token_packs.id'), nullable=False)
    tokens_amount = db.Column(db.Integer, nullable=False)
    price_paid = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('token_purchases', lazy=True))
    token_pack = db.relationship('TokenPack')
    
    def __repr__(self):
        return f'<TokenPurchase id={self.id} user_id={self.user_id} tokens={self.tokens_amount}>'