import os
import sys
from datetime import datetime, timedelta
import time
from flask import Flask
from models import db
from models.user import User
from models.wallet import Wallet
from models.product import Product
from models.auction import Auction
from models.bid import Bid
from tasks.auction_task import check_finished_auctions

def create_app():
    """Create a minimal Flask app for testing"""
    app = Flask(__name__)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction_site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def test_auction_completion():
    """Test that auctions properly complete when they reach end time"""
    app = create_app()
    
    with app.app_context():
        print("\n==== TESTING AUCTION COMPLETION PROCESS ====\n")
        
        # Create a test product if it doesn't exist
        product = Product.query.filter_by(name="Completion Test Product").first()
        if not product:
            product = Product(
                name="Completion Test Product",
                description="Product for testing auction completion",
                category="Test",
                is_active=True
            )
            db.session.add(product)
            db.session.commit()
        
        # Get some users for bidding
        users = User.query.filter(User.is_admin == False).limit(5).all()
        if len(users) < 5:
            print(f"Not enough users for testing. Found {len(users)}, need 5. Please create more users.")
            return
        
        # Create a short-running auction (ends in 10 seconds)
        end_time = datetime.utcnow() + timedelta(seconds=10)
        auction = Auction(
            product_id=product.id,
            product_name=product.name,
            product_description=product.description,
            product_price=10.0,
            start_time=datetime.utcnow(),
            end_time=end_time,
            current_price=10.0,
            token_cost_per_bid=1,
            is_active=True,
            status='active'
        )
        db.session.add(auction)
        db.session.commit()
        
        print(f"Created test auction: {auction.product_name} (ID: {auction.id})")
        print(f"Auction ends at: {auction.end_time}")
        
        # Clear any existing bids for this auction
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
        
        for i, bid_data in enumerate(bids_data):
            bid = Bid(
                auction_id=auction.id,
                user_id=bid_data["user"].id,
                amount=bid_data["amount"],
                created_at=datetime.utcnow()
            )
            db.session.add(bid)
        
        db.session.commit()
        
        print("Bids placed:")
        for bid_data in bids_data:
            print(f"User {bid_data['user'].username}: ${bid_data['amount']}")
        
        # Wait for auction to end
        seconds_to_wait = (end_time - datetime.utcnow()).total_seconds()
        if seconds_to_wait > 0:
            print(f"\nWaiting {seconds_to_wait:.1f} seconds for auction to end...")
            time.sleep(seconds_to_wait + 1)  # Add a buffer second
        
        print("\nAuction should be ended now. Running completion check...")
        
        # Before running completion task, verify state
        auction_before = db.session.get(Auction, auction.id)
        print(f"Before completion check - Status: {auction_before.status}, Is Active: {auction_before.is_active}")
        
        # Run the completion task
        check_finished_auctions(app)
        
        # Reload auction after completion
        db.session.refresh(auction)
        # Or alternatively:
        # auction = db.session.get(Auction, auction.id)
        
        print(f"\nAfter completion check - Status: {auction.status}, Is Active: {auction.is_active}")
        
        if auction.status == 'completed' and not auction.is_active:
            print("✅ Auction was correctly marked as completed!")
        else:
            print("❌ Auction was NOT correctly marked as completed.")
        
        # Check winner
        winner = auction.get_winner()
        
        if winner:
            print(f"\nDetermined winner: {winner.username}")
            winning_bid = Bid.query.filter_by(
                auction_id=auction.id, 
                user_id=winner.id
            ).order_by(Bid.amount.asc()).first()
            print(f"Winning bid amount: ${winning_bid.amount}")
            
            # Verify correct winner (should be user with $10.02 bid)
            expected_winner = users[1]
            if winner.id == expected_winner.id:
                print("✅ Correct winner was determined! (Lowest unique bid of $10.02)")
            else:
                print(f"❌ Incorrect winner. Expected {expected_winner.username}, got {winner.username}")
        else:
            print("❌ No winner was determined!")
        
        print("\n==== TEST COMPLETE ====")

if __name__ == "__main__":
    test_auction_completion()