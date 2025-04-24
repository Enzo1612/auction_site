from datetime import datetime

from models import db
from models.wallet import Wallet
from models.token_pack import TokenPack
from models.token_purchase import TokenPurchase

class TokenService:
    @staticmethod
    def get_active_token_packs():
        """Récupère les packs de jetons actifs"""
        return TokenPack.query.filter_by(is_active=True).order_by(TokenPack.token_count).all()
    
    @staticmethod
    def get_token_pack_by_id(pack_id):
        """Récupère un pack de jetons par son ID"""
        return TokenPack.query.get(pack_id)
    
    @staticmethod
    def purchase_token_pack(user_id, pack_id):
        """
        Achète un pack de jetons pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            pack_id: ID du pack de jetons
            
        Returns:
            (success, message): Tuple avec le statut de l'opération et un message
        """
        try:
            # Vérifier si le pack existe et est actif
            token_pack = TokenPack.query.filter_by(id=pack_id, is_active=True).first()
            if not token_pack:
                return False, "Ce pack de jetons n'existe pas ou n'est plus disponible."
            
            # Vérifier si l'utilisateur a un portefeuille
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not wallet:
                return False, "Portefeuille non trouvé."
            
            # Créer l'achat
            purchase = TokenPurchase(
                user_id=user_id,
                token_pack_id=pack_id,
                total_amount=token_pack.price
            )
            
            # Ajouter les jetons au portefeuille
            wallet.add_tokens(token_pack.token_count)
            
            db.session.add(purchase)
            db.session.commit()
            
            return True, f"Vous avez acheté {token_pack.token_count} jetons pour {token_pack.format_price()}."
            
        except Exception as e:
            db.session.rollback()
            return False, f"Une erreur est survenue: {str(e)}"
    
    @staticmethod
    def get_user_purchases(user_id):
        """Récupère l'historique des achats de jetons d'un utilisateur"""
        return TokenPurchase.query.filter_by(user_id=user_id).order_by(TokenPurchase.purchase_date.desc()).all()
    
    @staticmethod
    def create_token_pack(token_count, price_cents, description=None):
        """Crée un nouveau pack de jetons"""
        try:
            new_pack = TokenPack(
                token_count=token_count,
                price=price_cents,
                description=description
            )
            
            db.session.add(new_pack)
            db.session.commit()
            
            return True, "Le pack de jetons a été créé avec succès."
            
        except Exception as e:
            db.session.rollback()
            return False, f"Une erreur est survenue: {str(e)}"
            
    @staticmethod
    def update_token_pack(pack_id, token_count=None, price_cents=None, description=None, is_active=None):
        """Met à jour un pack de jetons"""
        try:
            pack = TokenPack.query.get(pack_id)
            if not pack:
                return False, "Ce pack de jetons n'existe pas."
            
            if token_count is not None:
                pack.token_count = token_count
                
            if price_cents is not None:
                pack.price = price_cents
                
            if description is not None:
                pack.description = description
                
            if is_active is not None:
                pack.is_active = is_active
                
            db.session.commit()
            
            return True, "Le pack de jetons a été mis à jour avec succès."
            
        except Exception as e:
            db.session.rollback()
            return False, f"Une erreur est survenue: {str(e)}"