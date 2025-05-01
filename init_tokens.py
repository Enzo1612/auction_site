from app import create_app
from models import db
from models.user import User
from models.wallet import Wallet
from models.token_pack import TokenPack
from flask_bcrypt import Bcrypt

def init_data():
    """Initialize data for the application."""
    app = create_app()
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        print("Initialisation des données...")
        
        # Créer un utilisateur admin
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                hashe_password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur admin créé!")
            
            # Créer un portefeuille pour l'admin
            admin_wallet = Wallet(
                user_id=admin.id,
                balance=100  # 100 jetons pour commencer
            )
            db.session.add(admin_wallet)
            db.session.commit()
            print("Portefeuille admin créé!")
        
        # Créer un utilisateur standard
        user = User.query.filter_by(email='user@example.com').first()
        if not user:
            user = User(
                username='user',
                email='user@example.com',
                hashed_password=bcrypt.generate_password_hash('user123').decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            print("Utilisateur standard créé!")
            
            # Créer un portefeuille pour l'utilisateur
            user_wallet = Wallet(
                user_id=user.id,
                balance=10  # 10 jetons pour commencer
            )
            db.session.add(user_wallet)
            db.session.commit()
            print("Portefeuille utilisateur créé!")
        
        # Créer les packs de jetons
        if TokenPack.query.count() == 0:
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
            print(f"{len(packs)} packs de jetons créés!")
        
        print("Initialisation terminée avec succès!")

if __name__ == '__main__':
    init_data()