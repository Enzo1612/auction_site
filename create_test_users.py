import os
import sys
import random
from datetime import datetime
from flask import Flask
from models import db
from models.user import User
from models.wallet import Wallet
from werkzeug.security import generate_password_hash

def create_app():
    """Create a minimal Flask app for database operations"""
    app = Flask(__name__)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction_site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def generate_random_users(num_users=10):
    """Create random test users with wallets"""
    app = create_app()
    
    # First names and last names for generating random user data
    first_names = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Charles", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth",
        "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Emma", "Olivia", "Ava", "Sophia"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee"
    ]
    
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "icloud.com"]
    
    with app.app_context():
        print(f"\n==== Creating {num_users} Test Users ====\n")
        
        created_users = []
        
        for i in range(num_users):
            # Generate random user data
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@{random.choice(domains)}"
            hashed_password = generate_password_hash("password123")  # All users have the same password
            
            # Check if username or email already exists
            if User.query.filter((User.username == username) | (User.email == email)).first():
                # If duplicate, try again with different random values
                continue
            
            try:
                # Try to create user with different possible field names
                user_data = {
                    "username": username,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_admin": False,
                    "is_active": True,
                    "created_at": datetime.utcnow()
                }
                
                # Check User model for password field name
                # Try common field names for password
                try:
                    # Examine User fields
                    user_columns = [column.name for column in User.__table__.columns]
                    print(f"Available User columns: {user_columns}")
                    
                    if "hashed_password" in user_columns:
                        user_data["hashed_password"] = hashed_password
                    elif "password_hash" in user_columns:
                        user_data["password_hash"] = hashed_password
                    elif "password" in user_columns:
                        user_data["password"] = hashed_password
                    else:
                        # If we can't determine the password field, let's print the model fields
                        raise ValueError(f"Could not determine password field name. Available fields: {user_columns}")
                        
                except Exception as e:
                    print(f"Error examining User model: {str(e)}")
                    # Fallback to using hashed_password
                    user_data["hashed_password"] = hashed_password
                
                # Create the user
                user = User(**user_data)
                
                db.session.add(user)
                db.session.flush()  # Flush to get the user ID
                
                # Create a wallet with random token balance
                wallet = Wallet(
                    user_id=user.id,
                    balance=random.randint(10, 100),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(wallet)
                created_users.append((user, wallet))
                
            except Exception as e:
                print(f"Error creating user {username}: {str(e)}")
                continue
        
        db.session.commit()
        
        # Print created users
        print(f"Created {len(created_users)} new users:")
        print("\nUsername | Email | Token Balance | Password")
        print("-" * 70)
        for user, wallet in created_users:
            print(f"{user.username} | {user.email} | {wallet.balance} tokens | password123")
        
        print("\n==== User Creation Complete ====")
        print("\nYou can log in with any of these accounts using password: password123")

if __name__ == "__main__":
    # Get number of users to create from command line or default to 10
    num_users = 10
    if len(sys.argv) > 1:
        try:
            num_users = int(sys.argv[1])
        except ValueError:
            print("Invalid number of users specified. Using default (10).")
    
    generate_random_users(num_users)