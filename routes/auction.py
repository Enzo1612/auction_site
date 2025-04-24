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

        # Vérifier si l'utilisateur a assez de jetons
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if not wallet or wallet.balance < auction.token_cost_per_bid:
            flash(f"Vous avez besoin de {auction.token_cost_per_bid} jeton(s) pour participer à cette enchère.", "error")
            return redirect(url_for('auction.detail', auction_id=auction_id))

        # Déduire les jetons du portefeuille
        wallet.balance -= auction.token_cost_per_bid

        # Créer la nouvelle enchère
        bid = Bid(
            auction_id=auction_id,
            user_id=current_user.id,
            amount=bid_amount
        )
        db.session.add(bid)

        # Enregistrer la transaction de jetons
        token_transaction = Transaction(
            user_id=current_user.id,
            description=f"Enchère placée sur {auction.product_name} ({bid_amount}€)",
            amount=-auction.token_cost_per_bid,
            balance=wallet.balance
        )
        db.session.add(token_transaction)

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
    
    return render_template('auctions/detail.html', 
                          auction=auction, 
                          bids=bids,
                          user=user)

@auction_bp.route('/')
def list_auctions():
    active_auctions = Auction.query.filter(
        Auction.status == 'active',
        Auction.end_time > datetime.utcnow()
    ).all()
    products = Product.query.all()  # Fetch all products
    return render_template('auctions/list.html', auctions=active_auctions, products=products)