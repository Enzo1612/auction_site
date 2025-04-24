from app import create_app
from models import db
from models.user import User

def promote_to_admin(email):
    """Promouvoir un utilisateur existant comme administrateur"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"Aucun utilisateur trouvé avec l'email: {email}")
            return
        
        if user.is_admin:
            print(f"L'utilisateur {user.username} est déjà administrateur.")
            return
        
        user.is_admin = True
        db.session.commit()
        print(f"L'utilisateur {user.username} (ID: {user.id}) a été promu administrateur.")

if __name__ == "__main__":
    email = input("Entrez l'email de l'utilisateur à promouvoir comme administrateur: ")
    promote_to_admin(email)