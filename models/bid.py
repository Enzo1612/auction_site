from models import db
from datetime import datetime

class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    refunded = db.Column(db.Boolean, default=False)  # Add this field
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    auction = db.relationship('Auction', back_populates='bids')
    user = db.relationship('User', back_populates='bids')

    def __repr__(self):
        return f"<Bid {self.id} - Auction {self.auction_id} - User {self.user_id} - Amount {self.amount}>"