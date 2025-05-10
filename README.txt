# Site d'Enchères au Centime Près

## Installation

1. Créer un environnement virtuel: `python -m venv venv`

2. Activer l'environnement virtuel:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

3. Installer les dépendances: `pip install -r requirements.txt`

4. Initialiser la base de données: `python scripts/create_clean_migration.py`

5. Créer un compte administrateur et configurer les packs de jetons: `python init_admin.py`

6. (Optionnel) Ajouter un utilisateur standard et des jetons supplémentaires: `python init_tokens.py`

## Utilisation

1. Lancer l'application: `python app.py`
ou: `flask run`

2. Accéder à l'application dans votre navigateur à l'adresse: http://127.0.0.1:5000

3. Se connecter avec les identifiants:
- Admin: admin@example.com / admin123
- Utilisateur standard (si créé): user@example.com / user123

## Fonctionnalités principales

- **Système d'enchères au centime près**: L'enchère la plus basse et unique remporte le produit
- **Gestion des jetons**: Les utilisateurs peuvent acheter des packs de jetons pour participer aux enchères
- **Tableau de bord administrateur**: Pour gérer les produits, les enchères et les packs de jetons
- **Historique des transactions**: Suivi de toutes les activités liées aux jetons
- **Système de portefeuille**: Solde de jetons par utilisateur pour participer aux enchères

## Remarques techniques

- Le site utilise Flask comme framework web
- SQLite est utilisé comme base de données pour simplifier le déploiement
- Un scheduler en arrière-plan vérifie automatiquement les enchères terminées

## Réinitialisation de la base de données

Si vous souhaitez réinitialiser complètement la base de données: `python reset_database.py`

Puis suivez les étapes 5-7 de l'installation pour reconfigurer les données.

## Auteurs

Nicaise Enzo - Selmin Loghan