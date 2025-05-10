from datetime import datetime
from flask import current_app
from sqlalchemy import func, and_

from models import db
from models.auction import Auction
from models.bid import Bid
from models.wallet import Wallet

class AuctionService:
    @staticmethod
    def get_active_auctions():
        """Récupère les enchères actives"""
        now = datetime.utcnow()
        return Auction.query.filter(
            and_(
                Auction.start_date <= now,
                Auction.end_time >= now,
                Auction.status == 'active'
            )
        ).order_by(Auction.end_time).all()
    
    @staticmethod
    def get_upcoming_auctions():
        """Récupère les enchères à venir"""
        now = datetime.utcnow()
        return Auction.query.filter(
            and_(
                Auction.start_date > now,
                Auction.status == 'pending'
            )
        ).order_by(Auction.start_date).all()
    
    @staticmethod
    def get_finished_auctions():
        """Récupère les enchères terminées"""
        return Auction.query.filter_by(status='finished').order_by(Auction.end_time.desc()).all()
    
    @staticmethod
    def get_auction_by_id(auction_id):
        """Récupère une enchère par son ID"""
        return Auction.query.get(auction_id)
    
    @staticmethod
    def place_bid(user_id, auction_id, amount_cents):
        """
        Place une enchère sur une enchère active
        
        Args:
            user_id: ID de l'utilisateur qui place l'enchère
            auction_id: ID de l'enchère
            amount_cents: Montant de l'enchère en centimes
            
        Returns:
            (success, message): Tuple avec le statut de l'opération et un message
        """
        try:

            auction = Auction.query.get(auction_id)
            if not auction or not auction.is_active():
                return False, "Cette enchère n'est pas active."
            

            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not wallet:
                return False, "Portefeuille non trouvé."
            
            if wallet.tokens < auction.token_cost_per_bid:
                return False, "Vous n'avez pas assez de jetons pour placer cette enchère."
            

            existing_bid = Bid.query.filter_by(
                user_id=user_id, 
                auction_id=auction_id, 
                amount=amount_cents
            ).first()
            
            if existing_bid:
                return False, "Vous avez déjà proposé ce montant pour cette enchère."
            
            
            new_bid = Bid(
                user_id=user_id,
                auction_id=auction_id,
                amount=amount_cents
            )
            
            wallet.use_tokens(auction.token_cost_per_bid)
            
            db.session.add(new_bid)
            db.session.commit()
            
            return True, "Votre enchère a été placée avec succès."
            
        except Exception as e:
            db.session.rollback()
            return False, f"Une erreur est survenue: {str(e)}"
    
    @staticmethod
    def get_user_bids(user_id, auction_id=None):
        """Récupère les enchères d'un utilisateur"""
        query = Bid.query.filter_by(user_id=user_id)
        
        if auction_id:
            query = query.filter_by(auction_id=auction_id)
            
        return query.order_by(Bid.created_at.desc()).all()
    
    @staticmethod
    def get_auction_stats(auction_id):
        """Récupère des statistiques sur une enchère"""
        total_bids = db.session.query(func.count(Bid.id)).filter_by(auction_id=auction_id).scalar()
        
        unique_bidders = db.session.query(func.count(func.distinct(Bid.user_id))).filter_by(auction_id=auction_id).scalar()
        

        unique_amounts = db.session.query(Bid.amount).filter_by(auction_id=auction_id).group_by(Bid.amount).having(func.count(Bid.id) == 1).count()
        
        return {
            'total_bids': total_bids,
            'unique_bidders': unique_bidders,
            'unique_amounts': unique_amounts
        }