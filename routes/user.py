from datetime import datetime
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from models import db
from models.auction import Auction
from models.bid import Bid
from models.wallet import Wallet
from models.transaction import Transaction

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile')
@login_required
def profile():
    """
    Display the user's profile.
    """
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/wallet')
@login_required
def wallet():
    """
    Display the user's wallet and recent transactions.
    """
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    if not wallet:
        flash("Wallet not found! Please contact support.", "danger")
        return redirect(url_for('main.home'))

    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(5).all()
    return render_template('user/wallet.html', wallet=wallet, transactions=transactions)

@user_bp.route('/history')
@login_required
def history():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    # Ajouter le portefeuille au contexte
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    
    if not wallet:
        # Créer un portefeuille si l'utilisateur n'en a pas
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()
    
    return render_template('user/history.html', transactions=transactions, wallet=wallet)

@user_bp.route('/add_funds', methods=['POST'])
@login_required
def add_funds():
    """
    Add funds to the user's wallet.
    """
    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash("Invalid amount. Please enter a positive value.", "danger")
            return redirect(url_for('user.wallet'))

        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if not wallet:
            flash("Wallet not found! Please contact support.", "danger")
            return redirect(url_for('main.home'))

        wallet.balance += amount

        transaction = Transaction(
            user_id=current_user.id,
            description="Deposit",
            amount=amount,
            balance=wallet.balance
        )
        db.session.add(transaction)
        db.session.commit()

        flash("Funds added successfully!", "success")
    except ValueError:
        flash("Invalid input. Please enter a valid number.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for('user.wallet'))

@user_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """
    Update the user's profile.
    """
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        current_user.first_name = first_name if first_name else current_user.first_name
        current_user.last_name = last_name if last_name else current_user.last_name
        current_user.username = username if username else current_user.username
        current_user.email = email if email else current_user.email

        if password:
            from werkzeug.security import generate_password_hash
            current_user.hashed_password = generate_password_hash(password)

        db.session.commit()
        flash("Your profile has been updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while updating your profile: {str(e)}", "danger")

    return redirect(url_for('user.profile'))

@user_bp.route('/my-bids')
@login_required
def my_bids():
    """
    Display all auctions the user has bid on.
    """
    # Get all unique auctions the user has bid on
    user_bids = db.session.query(Auction)\
        .join(Bid, Bid.auction_id == Auction.id)\
        .filter(Bid.user_id == current_user.id)\
        .distinct()\
        .order_by(Auction.end_time.desc())\
        .all()
    
    # Separate active and completed auctions
    active_auctions = []
    completed_auctions = []
    
    for auction in user_bids:
        if auction.status == 'active' and auction.is_active:
            active_auctions.append(auction)
        else:
            completed_auctions.append(auction)
            
    # For each auction, get the user's bids
    auction_bids = {}
    for auction in user_bids:
        bids = Bid.query.filter_by(
            auction_id=auction.id,
            user_id=current_user.id
        ).order_by(Bid.created_at.desc()).all()
        auction_bids[auction.id] = bids
    
    # Current datetime for countdown
    now = datetime.utcnow()
    
    return render_template(
        'user/my_bids.html',
        active_auctions=active_auctions,
        completed_auctions=completed_auctions,
        auction_bids=auction_bids,
        now=now
    )