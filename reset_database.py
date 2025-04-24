from app import create_app
from models import db
import os
import shutil
import time
import sys
import psutil  # Vous devrez peut-être installer cette bibliothèque: pip install psutil

def reset_database():
    print("=== Réinitialisation complète de la base de données ===")
    
    # Créer l'application
    app = create_app()
    
    with app.app_context():
        # 1. Supprimer la base de données existante
        db_path = os.path.join(app.instance_path, 'auction_site.db')
        if os.path.exists(db_path):
            print(f"Tentative de suppression de la base de données: {db_path}")
            try:
                os.remove(db_path)
                print("Base de données supprimée avec succès.")
            except PermissionError:
                print("Impossible de supprimer la base de données car elle est utilisée par un autre processus.")
                print("Tentative d'identifier et de fermer les processus qui l'utilisent...")
                
                # Liste des processus Python qui pourraient utiliser la base de données
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                            cmdline = ' '.join(proc.info['cmdline'] if proc.info['cmdline'] else [])
                            if 'flask' in cmdline or 'auction_site' in cmdline:
                                print(f"Processus trouvé: PID {proc.pid}, Commande: {cmdline}")
                                print(f"Veuillez terminer ce processus manuellement et réessayer.")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                print("\nVeuillez fermer toutes les instances de votre application et tous les outils")
                print("qui pourraient accéder à la base de données avant de continuer.")
                sys.exit(1)
        
        # 2. Supprimer les fichiers journal SQLite s'ils existent
        journal_path = db_path + '-journal'
        if os.path.exists(journal_path):
            try:
                os.remove(journal_path)
                print(f"Fichier journal supprimé: {journal_path}")
            except PermissionError:
                print(f"Impossible de supprimer le fichier journal: {journal_path}")
        
        # 3. Supprimer le dossier migrations
        migrations_path = os.path.join(os.path.dirname(app.instance_path), 'migrations')
        if os.path.exists(migrations_path):
            try:
                shutil.rmtree(migrations_path)
                print(f"Dossier migrations supprimé: {migrations_path}")
            except PermissionError:
                print(f"Impossible de supprimer le dossier migrations: {migrations_path}")
                print("Veuillez le supprimer manuellement.")
        
        # 4. Créer la base de données avec SQLAlchemy
        print("Création des tables avec SQLAlchemy...")
        db.create_all()
        print("Base de données créée avec succès!")
        
        print("\nMaintenant, vous pouvez exécuter:")
        print("1. flask db init")
        print("2. flask db migrate -m \"Initial migration\"")
        print("3. flask db upgrade")

if __name__ == "__main__":
    reset_database()