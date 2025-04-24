from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.token_pack import TokenPack
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
        # Créer un portefeuille pour l'utilisateur s'il n'en a pas
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
        # Créer un portefeuille pour l'utilisateur s'il n'en a pas
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()
    
    # Simuler le paiement (en production, vous ajouteriez ici une intégration de paiement réelle)
    try:
        # Enregistrer l'achat
        purchase = TokenPurchase(
            user_id=current_user.id,
            token_pack_id=pack.id,
            tokens_amount=pack.tokens,
            price_paid=pack.price
        )
        
        # Mettre à jour le solde du portefeuille
        wallet.balance += pack.tokens
        
        db.session.add(purchase)
        db.session.commit()
        
        flash(f"Achat réussi ! {pack.tokens} jetons ajoutés à votre portefeuille.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'achat : {str(e)}", "danger")
    
    return redirect(url_for('token.index'))

@token_bp.route('/history', methods=['GET'])
@login_required
def history():
    """
    Afficher l'historique des achats de jetons.
    """
    purchases = TokenPurchase.query.filter_by(user_id=current_user.id).order_by(TokenPurchase.created_at.desc()).all()
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    
    if not wallet:
        # Créer un portefeuille pour l'utilisateur s'il n'en a pas
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()
        flash("Un portefeuille a été créé pour vous.", "info")
    
    return render_template('tokens/history.html', purchases=purchases, wallet=wallet)