from app import create_app
from models import db
from models.user import User
from models.wallet import Wallet
from models.token_pack import TokenPack
from flask_bcrypt import Bcrypt

def init_admin():
    """Initialiser un utilisateur administrateur et des tokens packs"""
    app = create_app()
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        print("Création d'un utilisateur administrateur...")
        
        # Vérifier si un administrateur existe déjà
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            # Créer un utilisateur administrateur
            admin = User(
                username='admin',
                email='admin@example.com',
                hashed_password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Utilisateur administrateur créé avec ID: {admin.id}")
            
            # Créer un portefeuille pour l'administrateur
            admin_wallet = Wallet(
                user_id=admin.id,
                balance=100  # L'administrateur commence avec 100 jetons
            )
            db.session.add(admin_wallet)
            db.session.commit()
            print("Portefeuille administrateur créé avec 100 jetons")
        else:
            print(f"Un administrateur existe déjà (ID: {admin.id})")
        
        # Créer des packs de jetons si nécessaire
        if TokenPack.query.count() == 0:
            print("Création des packs de jetons...")
            packs = [
                TokenPack(name="Pack Débutant", tokens=10, price=1.99, discount_percentage=0),
                TokenPack(name="Pack Standard", tokens=50, price=8.99, discount_percentage=10),
                TokenPack(name="Pack Premium", tokens=120, price=19.99, discount_percentage=15),
                TokenPack(name="Pack Or", tokens=250, price=39.99, discount_percentage=20),
                TokenPack(name="Pack Platine", tokens=500, price=69.99, discount_percentage=30),
                TokenPack(name="Pack VIP", tokens=1000, price=119.99, discount_percentage=40),
            ]
            
            db.session.add_all(packs)
            db.session.commit()
            print(f"{len(packs)} packs de jetons créés")
        else:
            print("Des packs de jetons existent déjà")

if __name__ == "__main__":
    init_admin()