import os
import sys
import random
from datetime import datetime, timedelta
from flask import Flask
from models import db
from models.product import Product
from models.auction import Auction

def create_app():
    """Create a minimal Flask app for database operations"""
    app = Flask(__name__)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction_site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def generate_random_auctions(num_auctions=20):
    """Create random test auctions"""
    app = create_app()
    
    with app.app_context():
        print(f"\n==== Creating {num_auctions} Test Auctions ====\n")
        
        # Get available products
        products = Product.query.filter_by(is_active=True).all()
        
        if not products:
            print("No products found in the database. Please run seed_products.py first.")
            return
        
        created_auctions = []
        
        # Generate random durations
        durations = [
            {"hours": 1},
            {"days": 1},
            {"days": 3},
            {"days": 7},
            {"days": 14},
            {"minutes": 30}
        ]
        
        # Generate token costs
        token_costs = [1, 2, 3, 5, 10]
        
        for i in range(num_auctions):
            # Select a random product
            product = random.choice(products)
            
            # Generate a random start time between now and 7 days ago
            start_time_offset = random.randint(0, 7*24*60*60)  # Random seconds up to 7 days
            start_time = datetime.utcnow() - timedelta(seconds=start_time_offset)
            
            # Choose a random duration
            duration = random.choice(durations)
            
            # Calculate end time
            end_time = start_time + timedelta(**duration)
            
            # Generate random starting price
            base_price = random.uniform(10.0, 1000.0)
            start_price = round(base_price, 2)
            
            # Choose random token cost
            token_cost = random.choice(token_costs)
            
            # Determine if auction should be active or completed
            is_active = end_time > datetime.utcnow()
            status = 'active' if is_active else 'completed'
            
            # Create the auction
            auction = Auction(
                product_id=product.id,
                product_name=product.name,
                product_description=product.description,
                product_price=start_price,
                start_time=start_time,
                end_time=end_time,
                current_price=start_price,
                token_cost_per_bid=token_cost,
                is_active=is_active,
                status=status
            )
            
            db.session.add(auction)
            created_auctions.append({
                "product": product.name,
                "start_price": start_price,
                "token_cost": token_cost,
                "start_time": start_time,
                "end_time": end_time,
                "status": status
            })
        
        db.session.commit()
        
        # Print created auctions
        print(f"Successfully created {len(created_auctions)} auctions:\n")
        
        for i, auction in enumerate(created_auctions):
            duration = auction["end_time"] - auction["start_time"]
            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            duration_str = ""
            if days > 0:
                duration_str += f"{days} days "
            if hours > 0:
                duration_str += f"{hours} hours "
            if minutes > 0:
                duration_str += f"{minutes} minutes"
                
            print(f"{i+1}. {auction['product']}")
            print(f"   Price: ${auction['start_price']:.2f}")
            print(f"   Token Cost: {auction['token_cost']} tokens per bid")
            print(f"   Duration: {duration_str}")
            print(f"   Status: {auction['status'].upper()}")
            print()
        
        # Count active vs completed
        active_count = sum(1 for a in created_auctions if a["status"] == "active")
        completed_count = len(created_auctions) - active_count
        
        print(f"Active auctions: {active_count}")
        print(f"Completed auctions: {completed_count}")
        print("\n==== Auction Creation Complete ====")

if __name__ == "__main__":
    # Get number of auctions to create from command line or default to 20
    num_auctions = 20
    if len(sys.argv) > 1:
        try:
            num_auctions = int(sys.argv[1])
        except ValueError:
            print("Invalid number of auctions specified. Using default (20).")
    
    generate_random_auctions(num_auctions)