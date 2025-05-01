from models import db
from datetime import datetime
from models.bid import Bid
from models.transaction import Transaction
from models.user import User
from models.wallet import Wallet
from sqlalchemy import func, and_

class Auction(db.Model):
    __tablename__ = "auctions"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    product_description = db.Column(db.Text, nullable=True)
    product_price = db.Column(db.Float, nullable=False)  # Prix minimum pour les enchères
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')
    token_cost_per_bid = db.Column(db.Integer, default=1)  # Nombre de jetons par enchère
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    product = db.relationship('Product', back_populates='auctions')
    bids = db.relationship('Bid', back_populates='auction', lazy='dynamic', cascade="all, delete-orphan")

    def get_winner(self):
        """
        Determine the winner of the auction based on lowest unique bid.
        Returns the User object of the winner, or None if no winner.
        """
        # Get all bids for this auction
        all_bids = Bid.query.filter_by(auction_id=self.id).all()
        
        # Count occurrences of each bid amount
        bid_counts = {}
        for bid in all_bids:
            if bid.amount in bid_counts:
                bid_counts[bid.amount] += 1
            else:
                bid_counts[bid.amount] = 1
        
        # Filter for unique bids (count = 1)
        unique_bids = {amount: count for amount, count in bid_counts.items() if count == 1}
        
        if not unique_bids:
            return None  # No unique bids
        
        # Find the lowest unique bid
        lowest_unique_bid_amount = min(unique_bids.keys())
        
        # Find the user who placed this bid
        winning_bid = Bid.query.filter_by(
            auction_id=self.id,
            amount=lowest_unique_bid_amount
        ).first()
        
        return User.query.get(winning_bid.user_id) if winning_bid else None

    def refund_non_winning_bidders(self):
        """
        Rembourse les jetons à tous les utilisateurs qui n'ont pas gagné.
        """
        winner = self.get_winner()
        # Le vainqueur est celui avec la plus basse enchère unique
        for bid in self.bids.filter_by(refunded=False).all():
            # Rembourser tous les utilisateurs sauf le gagnant
            if not winner or bid.user_id != winner.id:
                # Rembourser les jetons à l'utilisateur
                wallet = Wallet.query.filter_by(user_id=bid.user_id).first()
                if wallet:
                    wallet.balance += self.token_cost_per_bid
                    
                    # Créer une transaction pour le remboursement
                    refund_transaction = Transaction(
                        user_id=bid.user_id,
                        description=f"Remboursement de jetons pour enchère non gagnante sur '{self.product_name}'",
                        amount=self.token_cost_per_bid,
                        balance=wallet.balance
                    )
                    db.session.add(refund_transaction)
                    
                # Marquer l'enchère comme remboursée
                bid.refunded = True
                
        db.session.commit()

    def __repr__(self):
        return f'<Auction {self.id} - {self.product_name}>'