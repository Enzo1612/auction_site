from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.auction import Auction
from models.product import Product
from models.bid import Bid
from models.transaction import Transaction
from models.wallet import Wallet
from flask_login import current_user, login_required
from datetime import datetime, timedelta

auction_bp = Blueprint('auction', __name__, url_prefix='/auctions')

@auction_bp.route('/create', methods=['POST'])
@login_required
def create():
    """
    Create a new auction (Admin only).
    """
    if not current_user.is_admin:
        flash("Only admins can create auctions.", "danger")
        return redirect(url_for('auction.list_auctions'))

    product_id = request.form.get('product_id')
    product_price = request.form.get('product_price')
    token_cost = request.form.get('token_cost_per_bid', 1)
    duration_days = request.form.get('duration_days')
    duration_hours = request.form.get('duration_hours')

    # Validate form fields
    if not product_id or not product_price or not duration_days or not duration_hours:
        flash("All fields are required.", "error")
        return redirect(url_for('auction.list_auctions'))

    try:
        # Check if the product exists
        product = Product.query.get(product_id)
        if not product:
            flash("Invalid product selected.", "error")
            return redirect(url_for('auction.list_auctions'))

        # Calculate the end time based on the duration
        end_time = datetime.utcnow() + timedelta(days=int(duration_days), hours=int(duration_hours))

        # Create a new auction
        auction = Auction(
            product_id=product.id,
            product_name=product.name,
            product_description=product.description,
            product_price=float(product_price),
            start_time=datetime.utcnow(),
            end_time=end_time,
            current_price=float(product_price),
            token_cost_per_bid=int(token_cost),
            is_active=True,
            status='active'
        )
        db.session.add(auction)
        db.session.commit()
        flash("Auction created successfully.", "success")
        return redirect(url_for('admin.auctions'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating auction: {str(e)}", "error")
        return redirect(url_for('admin.auctions'))

@auction_bp.route('/<int:auction_id>/bid', methods=['POST'])
@login_required
def bid(auction_id):
    """
    Place a bid on an auction.
    """
    bid_amount = request.form.get('bid_amount')

    if not bid_amount:
        flash("Bid amount is required.", "error")
        return redirect(url_for('auction.detail', auction_id=auction_id))

    try:
        auction = Auction.query.get_or_404(auction_id)
        bid_amount = float(bid_amount)
        
        # Vérifier que l'enchère est active
        if auction.status != 'active' or auction.end_time <= datetime.utcnow():
            flash("Cette enchère n'est plus active.", "error")
            return redirect(url_for('auction.detail', auction_id=auction_id))

        # Vérifier que le montant est supérieur au prix minimum
        if bid_amount < auction.product_price:
            flash(f"Le montant de l'enchère doit être d'au moins {auction.product_price}€.", "error")
            return redirect(url_for('auction.detail', auction_id=auction_id))

        # Vérifier si l'utilisateur a déjà proposé ce montant
        existing_bid = Bid.query.filter_by(
            auction_id=auction_id,
            user_id=current_user.id,
            amount=bid_amount
        ).first()
        
        if existing_bid:
            flash("Vous avez déjà proposé ce montant pour cette enchère.", "error")
            return redirect(url_for('auction.detail', auction_id=auction_id))

        # Vérifier si quelqu'un d'autre a déjà misé ce montant (pour centime-près)
        existing_bid_from_others = Bid.query.filter_by(
            auction_id=auction_id,
            amount=bid_amount
        ).first()
        
        if existing_bid_from_others:
            flash("Ce montant a déjà été proposé par un autre utilisateur.", "error")
            return redirect(url_for('auction.detail', auction_id=auction_id))

        # Vérifier si l'utilisateur a assez de jetons
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if not wallet or wallet.balance < auction.token_cost_per_bid:
            flash(f"Vous avez besoin de {auction.token_cost_per_bid} jeton(s) pour participer à cette enchère.", "error")
            return redirect(url_for('auction.detail', auction_id=auction_id))

        # Déduire les jetons du portefeuille
        wallet.balance -= auction.token_cost_per_bid

        # Créer la nouvelle enchère
        new_bid = Bid(
            auction_id=auction_id,
            user_id=current_user.id,
            amount=bid_amount,
            created_at=datetime.utcnow()
        )
        db.session.add(new_bid)

        # Enregistrer la transaction de jetons
        token_transaction = Transaction(
            user_id=current_user.id,
            auction_id=auction_id,
            type='bid',
            description=f"Enchère placée sur {auction.product_name} ({bid_amount}€)",
            amount=-auction.token_cost_per_bid,
            balance=wallet.balance,
            created_at=datetime.utcnow()
        )
        db.session.add(token_transaction)

        # Mettre à jour le prix courant si c'est la plus basse enchère unique
        # Récupérer toutes les enchères pour cette vente
        all_bids = Bid.query.filter_by(auction_id=auction_id).all()
        
        # Regrouper les montants par le nombre de fois qu'ils apparaissent
        bid_counts = {}
        for b in all_bids:
            if b.amount in bid_counts:
                bid_counts[b.amount] += 1
            else:
                bid_counts[b.amount] = 1
        
        # Trouver les enchères uniques (apparaissant une seule fois)
        unique_bids = [amount for amount, count in bid_counts.items() if count == 1]
        
        # Si l'enchère actuelle est unique et est inférieure au prix actuel, la définir comme nouvelle enchère gagnante
        if bid_amount in unique_bids and (auction.current_price is None or bid_amount < auction.current_price):
            auction.current_price = bid_amount
            auction.current_winner_id = current_user.id

        db.session.commit()
        flash("Votre enchère a été placée avec succès.", "success")
        return redirect(url_for('auction.detail', auction_id=auction_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors du placement de l'enchère: {str(e)}", "error")
        return redirect(url_for('auction.detail', auction_id=auction_id))
    
@auction_bp.route('/<int:auction_id>')
def detail(auction_id):
    """
    View details of a specific auction.
    """
    auction = Auction.query.get_or_404(auction_id)
    bids = auction.bids.order_by(Bid.created_at.desc()).all()
    
    # Pour l'utilisateur connecté, récupérer son portefeuille
    user = None
    if current_user.is_authenticated:
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        user = {
            'wallet_balance': wallet.balance if wallet else 0
        }
    
    # Calculate unique bids
    bid_counts = {}
    for b in bids:
        if b.amount in bid_counts:
            bid_counts[b.amount] += 1
        else:
            bid_counts[b.amount] = 1
    
    unique_bids = [amount for amount, count in bid_counts.items() if count == 1]
    
    return render_template('auctions/detail.html', 
                          auction=auction, 
                          bids=bids,
                          user=user,
                          unique_bids=unique_bids)

@auction_bp.route('/')
def list_auctions():
    """
    List all active auctions.
    """
    active_auctions = Auction.query.filter(
        Auction.status == 'active',
        Auction.end_time > datetime.utcnow()
    ).all()
    products = Product.query.all()  # Fetch all products
    return render_template('auctions/list.html', auctions=active_auctions, products=products)

@auction_bp.route('/completed')
def completed_auctions():
    """
    List completed auctions.
    """
    completed_auctions = Auction.query.filter(
        Auction.status == 'completed'
    ).order_by(Auction.end_time.desc()).all()
    
    return render_template('auctions/completed.html', auctions=completed_auctions)

@auction_bp.route('/refund/<int:bid_id>', methods=['POST'])
@login_required
def refund_bid(bid_id):
    """
    Refund tokens for a bid (admin only or if auction is cancelled).
    """
    if not current_user.is_admin:
        flash("Only administrators can issue refunds.", "error")
        return redirect(url_for('main.home'))
        
    try:
        bid = Bid.query.get_or_404(bid_id)
        auction = Auction.query.get_or_404(bid.auction_id)
        
        # Check if refund is allowed (auction cancelled or admin decision)
        if auction.status != 'cancelled' and not current_user.is_admin:
            flash("Les remboursements ne sont autorisés que pour les enchères annulées.", "error")
            return redirect(url_for('auction.detail', auction_id=auction.id))
            
        # Refund tokens to the user's wallet
        wallet = Wallet.query.filter_by(user_id=bid.user_id).first()
        if wallet:
            wallet.balance += auction.token_cost_per_bid
            
            # Record the refund transaction
            refund_transaction = Transaction(
                user_id=bid.user_id,
                auction_id=auction.id,
                type='refund',
                description=f"Remboursement pour enchère sur {auction.product_name}",
                amount=auction.token_cost_per_bid,
                balance=wallet.balance,
                created_at=datetime.utcnow()
            )
            
            db.session.add(refund_transaction)
            db.session.commit()
            
            flash(f"Remboursement de {auction.token_cost_per_bid} jetons effectué avec succès.", "success")
        else:
            flash("Impossible de trouver le portefeuille de l'utilisateur.", "error")
            
        return redirect(url_for('auction.detail', auction_id=auction.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors du remboursement: {str(e)}", "error")
        return redirect(url_for('main.home'))