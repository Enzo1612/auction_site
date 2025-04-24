import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app  # Import your Flask app factory
from models import db
from models.user import User
from werkzeug.security import generate_password_hash

def create_admin():
    admin_username = "admin"
    admin_email = "admin@example.com"
    admin_password = "admin123"  # Change this to a secure password

    # Check if admin already exists
    existing_admin = User.query.filter_by(username=admin_username).first()
    if existing_admin:
        print("Admin user already exists.")
        return

    # Create a new admin user
    admin_user = User(
        first_name="Admin",
        last_name="User",
        username=admin_username,
        email=admin_email,
        hashed_password=generate_password_hash(admin_password),
        is_admin=True
    )
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully!")

if __name__ == "__main__":
    app = create_app()  # Create the Flask app
    with app.app_context():  # Set the application context
        create_admin()