from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.auction import Auction
from models.bid import Bid
from models.product import Product
from models.token_pack import TokenPack
from models.transaction import Transaction
from models.wallet import Wallet
from models.token_purchase import TokenPurchase

token_bp = Blueprint('token', __name__, url_prefix='/tokens')

@token_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Afficher les packs de jetons disponibles.
    """
    packs = TokenPack.query.filter_by(is_active=True).order_by(TokenPack.tokens).all()
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    
    if not wallet:

        wallet = Wallet(user_id=current_user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()
        flash("Un portefeuille a été créé pour vous.", "info")
    
    return render_template('tokens/index.html', packs=packs, wallet=wallet)

@token_bp.route('/purchase/<int:pack_id>', methods=['POST'])
@login_required
def purchase(pack_id):
    """
    Acheter un pack de jetons.
    """
    pack = TokenPack.query.get_or_404(pack_id)
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    
    if not wallet:

        wallet = Wallet(user_id=current_user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()

    try:

        purchase = TokenPurchase(
            user_id=current_user.id,
            token_pack_id=pack.id,
            tokens_amount=pack.tokens,
            price_paid=pack.price
        )
        

        wallet.balance += pack.tokens
        
        db.session.add(purchase)
        db.session.commit()
        
        flash(f"Achat réussi ! {pack.tokens} jetons ajoutés à votre portefeuille.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'achat : {str(e)}", "danger")
    
    return redirect(url_for('token.index'))

@token_bp.route('/history')
@login_required
def history():
    """
    Display the user's token transaction history.
    """
    # Get token purchases
    purchases = TokenPurchase.query.filter_by(user_id=current_user.id).order_by(TokenPurchase.created_at.desc()).all()
    
    # Get token usage from bids
    bid_token_usage = db.session.query(
        Bid.id,
        Bid.created_at,
        Bid.amount,
        Auction.id.label('auction_id'),
        Auction.token_cost_per_bid,
        Auction.product_name
    ).join(
        Auction, Bid.auction_id == Auction.id
    ).filter(
        Bid.user_id == current_user.id
    ).order_by(
        Bid.created_at.desc()
    ).all()

    refunds = []
    try:

        refunds = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.description.like('%Remboursement%')
        ).order_by(
            Transaction.created_at.desc()
        ).all()
    except Exception:

        refunds = []
    
    # Combine all activities into one timeline
    all_activities = []
    
    # Add purchases
    for purchase in purchases:
        all_activities.append({
            'id': purchase.id,
            'date': purchase.created_at,
            'type': 'purchase',
            'tokens': purchase.tokens_amount,  # Use tokens_amount from model
            'amount': purchase.price_paid,
            'description': f"Achat de {purchase.tokens_amount} jetons",
            'product_name': None
        })
    
    # Add bid token usage
    for bid in bid_token_usage:
        all_activities.append({
            'id': bid.id,
            'date': bid.created_at,
            'type': 'bid',
            'tokens': -bid.token_cost_per_bid,  # Negative since tokens are spent
            'amount': bid.amount,
            'description': f"Enchère de {bid.amount} € sur {bid.product_name}",
            'product_name': bid.product_name
        })
    
    # Add refunds
    for refund in refunds:
        token_amount = getattr(refund, 'amount', 0)
        description = getattr(refund, 'description', "Remboursement de jetons")
        product_name = None
        
        all_activities.append({
            'id': refund.id,
            'date': refund.created_at,
            'type': 'refund',
            'tokens': token_amount,  # Positive since tokens are returned
            'amount': 0,
            'description': description,
            'product_name': product_name
        })
    
    # Sort all activities by date, most recent first
    all_activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Get current wallet balance
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    
    return render_template('tokens/history.html', 
                          activities=all_activities, 
                          wallet=wallet)