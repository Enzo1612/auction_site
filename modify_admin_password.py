from app import create_app
from models import db
from models.user import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    """Reset the admin password with werkzeug's hashing method"""
    app = create_app()
    
    with app.app_context():
        # Trouver l'utilisateur admin
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("Aucun administrateur trouvé!")
            return
            
        # Définir un nouveau mot de passe avec la méthode werkzeug
        new_password = "admin123"  # Vous pouvez changer cela si vous le souhaitez
        admin.hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        db.session.commit()
        print(f"Mot de passe de l'administrateur {admin.username} réinitialisé avec succès.")
        print(f"Nouveau mot de passe: {new_password}")

if __name__ == "__main__":
    reset_admin_password()