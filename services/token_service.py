from datetime import datetime

from models import db
from models.wallet import Wallet
from models.token_pack import TokenPack
from models.token_purchase import TokenPurchase

class TokenService:
    """
    Service class that handles token-related operations including:
    - Token pack management
    - Token purchases
    - Token wallet operations
    
    This service centralizes token business logic away from routes.
    """
    
    @staticmethod
    def get_active_token_packs():
        """
        Retrieves all active token packs, ordered by token count.
        
        Returns:
            list: All active token packs sorted by token count in ascending order.
        """
        return TokenPack.query.filter_by(is_active=True).order_by(TokenPack.tokens).all()
    
    @staticmethod
    def get_token_pack_by_id(pack_id):
        """
        Retrieves a token pack by its ID.
        
        Args:
            pack_id (int): The ID of the token pack to retrieve.
            
        Returns:
            TokenPack: The token pack with the specified ID, or None if not found.
        """
        return TokenPack.query.get(pack_id)
    
    @staticmethod
    def purchase_token_pack(user_id, pack_id):
        """
        Processes a token pack purchase for a user.
        This includes creating a purchase record and adding tokens to user's wallet.
        
        Args:
            user_id (int): ID of the user making the purchase
            pack_id (int): ID of the token pack being purchased
            
        Returns:
            tuple: (success, message) - success is a boolean indicating if the operation succeeded,
                   message is a string with details about the result.
        """
        try:
            # Check if the pack exists and is active
            token_pack = TokenPack.query.filter_by(id=pack_id, is_active=True).first()
            if not token_pack:
                return False, "This token pack doesn't exist or is no longer available."
            
            # Check if the user has a wallet
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not wallet:
                return False, "Wallet not found."
            
            # Create the purchase record
            purchase = TokenPurchase(
                user_id=user_id,
                token_pack_id=pack_id,
                tokens_amount=token_pack.tokens,
                price_paid=token_pack.price
            )
            
            # Add tokens to the wallet
            wallet.balance += token_pack.tokens
            
            db.session.add(purchase)
            db.session.commit()
            
            return True, f"You have purchased {token_pack.tokens} tokens for {token_pack.formatted_price()}."
            
        except Exception as e:
            db.session.rollback()
            return False, f"An error occurred: {str(e)}"
    
    @staticmethod
    def get_user_purchases(user_id):
        """
        Retrieves the token purchase history for a user.
        
        Args:
            user_id (int): The ID of the user.
            
        Returns:
            list: User's token purchases ordered by date, most recent first.
        """
        return TokenPurchase.query.filter_by(user_id=user_id).order_by(TokenPurchase.created_at.desc()).all()
    
    @staticmethod
    def create_token_pack(name, tokens, price, discount_percentage=0, description=None):
        """
        Creates a new token pack with the specified parameters.
        
        Args:
            name (str): The name of the token pack (e.g., "Basic Pack")
            tokens (int): Number of tokens in the pack
            price (float): Price of the pack in euros
            discount_percentage (float, optional): Discount percentage. Defaults to 0.
            description (str, optional): Description of the token pack. Defaults to None.
            
        Returns:
            tuple: (success, message) - success is a boolean indicating if the operation succeeded,
                   message is a string with details about the result.
        """
        try:
            new_pack = TokenPack(
                name=name,
                tokens=tokens,
                price=price,
                discount_percentage=discount_percentage
            )
            
            db.session.add(new_pack)
            db.session.commit()
            
            return True, "The token pack was successfully created."
            
        except Exception as e:
            db.session.rollback()
            return False, f"An error occurred: {str(e)}"
            
    @staticmethod
    def update_token_pack(pack_id, name=None, tokens=None, price=None, discount_percentage=None, is_active=None):
        """
        Updates an existing token pack with the provided parameters.
        Only updates fields that are not None.
        
        Args:
            pack_id (int): ID of the token pack to update
            name (str, optional): New name for the token pack
            tokens (int, optional): New number of tokens
            price (float, optional): New price
            discount_percentage (float, optional): New discount percentage
            is_active (bool, optional): New active status
            
        Returns:
            tuple: (success, message) - success is a boolean indicating if the operation succeeded,
                   message is a string with details about the result.
        """
        try:
            pack = TokenPack.query.get(pack_id)
            if not pack:
                return False, "This token pack doesn't exist."
            
            if name is not None:
                pack.name = name
                
            if tokens is not None:
                pack.tokens = tokens
                
            if price is not None:
                pack.price = price
                
            if discount_percentage is not None:
                pack.discount_percentage = discount_percentage
                
            if is_active is not None:
                pack.is_active = is_active
                
            pack.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, "The token pack was successfully updated."
            
        except Exception as e:
            db.session.rollback()
            return False, f"An error occurred: {str(e)}"