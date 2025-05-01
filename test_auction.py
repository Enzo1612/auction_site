import os
import sys
from datetime import datetime, timedelta
import random
from flask import Flask
from models import db
from models.user import User
from models.wallet import Wallet
from models.product import Product
from models.auction import Auction
from models.bid import Bid
from models.transaction import Transaction
from tasks.auction_task import check_finished_auctions

def create_app():
    """Create a minimal Flask app for testing"""
    app = Flask(__name__)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction_site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def test_winner_determination():
    """Test just the winner determination logic"""
    app = create_app()
    
    with app.app_context():
        print("\n==== TESTING WINNER DETERMINATION LOGIC ====\n")
        
        # Create a test product if it doesn't exist
        product = Product.query.filter_by(name="Test Winner Logic").first()
        if not product:
            product = Product(
                name="Test Winner Logic",
                description="Product for testing winner determination",
                category="Test",
                is_active=True
            )
            db.session.add(product)
            db.session.commit()
        
        # Create a test auction
        auction = Auction(
            product_id=product.id,
            product_name=product.name,
            product_description=product.description,
            product_price=10.0,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() - timedelta(minutes=5),  # Already ended
            current_price=10.0,
            token_cost_per_bid=1,
            is_active=False,
            status='completed'
        )
        db.session.add(auction)
        db.session.commit()
        
        # Get some users
        users = User.query.filter(User.is_admin == False).limit(5).all()
        if len(users) < 5:
            print(f"Not enough users for testing. Found {len(users)}, need 5. Please create more users.")
            return
        
        # First delete any existing bids for this auction to start clean
        Bid.query.filter_by(auction_id=auction.id).delete()
        db.session.commit()
        
        # Create bids with a clear lowest unique bid pattern
        # User 1: bids $10.01 (not unique - duplicate with User 4)
        # User 2: bids $10.02 (unique - should be winner)
        # User 3: bids $10.03 (not unique - duplicate with User 5)
        # User 4: bids $10.01 (not unique - duplicate with User 1)
        # User 5: bids $10.03 (not unique - duplicate with User 3)
        bids_data = [
            {"user": users[0], "amount": 10.01},  # Not unique
            {"user": users[1], "amount": 10.02},  # Unique - SHOULD WIN
            {"user": users[2], "amount": 10.03},  # Not unique
            {"user": users[3], "amount": 10.01},  # Not unique (duplicate)
            {"user": users[4], "amount": 10.03},  # Not unique (duplicate)
        ]
        
        print("Creating test bids...")
        for i, bid_data in enumerate(bids_data):
            bid = Bid(
                auction_id=auction.id,
                user_id=bid_data["user"].id,
                amount=bid_data["amount"],
                created_at=datetime.utcnow() - timedelta(minutes=10) + timedelta(seconds=i)
            )
            db.session.add(bid)
        
        db.session.commit()
        
        print("Bids placed:")
        for bid_data in bids_data:
            print(f"User {bid_data['user'].username}: ${bid_data['amount']}")
        
        print("\nAnalyzing unique bids:")
        all_bids = Bid.query.filter_by(auction_id=auction.id).all()
        bid_counts = {}
        for bid in all_bids:
            if bid.amount in bid_counts:
                bid_counts[bid.amount] += 1
            else:
                bid_counts[bid.amount] = 1
        
        for amount, count in bid_counts.items():
            unique = "UNIQUE" if count == 1 else "not unique"
            print(f"${amount}: {count} bids - {unique}")
        
        print("\nDetermining winner based on lowest unique bid...")
        winner = auction.get_winner()
        
        if winner:
            print(f"Winner: {winner.username}")
            winning_bid = Bid.query.filter_by(
                auction_id=auction.id,
                user_id=winner.id
            ).order_by(Bid.amount.asc()).first()
            print(f"Winning Bid Amount: ${winning_bid.amount}")
            
            # Verify this is actually the lowest unique bid
            expected_winner = users[1]  # Should be user 2 with a bid of $10.02
            if winner.id == expected_winner.id:
                print("✅ Winner determination is CORRECT! (Lowest unique bid is $10.02)")
            else:
                print(f"❌ Winner determination is INCORRECT! Expected {expected_winner.username}, got {winner.username}")
        else:
            print("No winner determined")
        
        print("\n==== TEST COMPLETE ====")

if __name__ == "__main__":
    test_winner_determination()