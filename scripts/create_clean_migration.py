from app import create_app, db
from flask_migrate import Migrate

def create_clean_migration():
    app = create_app()
    
    migrate = Migrate(app, db)
    
    with app.app_context():
        db.create_all()
        
        print("Base de données créée avec succès!")

if __name__ == "__main__":
    create_clean_migration()