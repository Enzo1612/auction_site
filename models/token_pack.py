from models import db
from datetime import datetime

class TokenPack(db.Model):
    __tablename__ = "token_packs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tokens = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @property
    def price_per_token(self):
        """Calculer le prix par jeton."""
        if self.tokens > 0:
            return self.price / self.tokens
        return 0
    
    def __repr__(self):
        return f'<TokenPack id={self.id} name={self.name} tokens={self.tokens}>'