from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from models import db
from models.auction import Auction
from models.bid import Bid
from models.product import Product
from models.token_pack import TokenPack
from models.user import User
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """
    Decorator to ensure the user is an admin.
    """
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard route.
    """
    users = User.query.all()
    active_auctions = Auction.query.filter(Auction.is_active == True).all()
    products = Product.query.all()

    # Fetch recent activity
    recent_activity = []

    # Add recently created auctions
    recent_auctions = Auction.query.order_by(Auction.created_at.desc()).limit(5).all()
    for auction in recent_auctions:
        recent_activity.append({
            'type': 'created',
            'message': f"New auction created: {auction.product_name}",
            'timestamp': auction.created_at
        })

    # Add recently finished auctions
    finished_auctions = Auction.query.filter(Auction.is_active == False).order_by(Auction.end_time.desc()).limit(5).all()
    for auction in finished_auctions:
        winner = auction.get_winner()
        winner_message = f"Winner: {winner.username}" if winner else "No winner"
        recent_activity.append({
            'type': 'finished',
            'message': f"Auction finished: {auction.product_name} ({winner_message})",
            'timestamp': auction.end_time
        })

    # Sort recent activity by timestamp (most recent first)
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template(
        'admin/dashboard.html',
        users=users,
        active_auctions=active_auctions,
        products=products,
        recent_activity=recent_activity
    )



@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """
    View details of a specific user.
    """
    user = User.query.get_or_404(user_id)
    return render_template('admin/detail.html', user=user)

@admin_bp.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    """
    Update a user's details.
    """
    user = User.query.get_or_404(user_id)
    try:
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        user.is_active = 'is_active' in request.form
        user.is_admin = 'is_admin' in request.form

        # Update wallet balance
        wallet_balance = request.form.get('wallet_balance')
        if wallet_balance is not None:
            user.wallet.balance = float(wallet_balance)

        # Update password if provided
        password = request.form.get('password')
        if password:
            from werkzeug.security import generate_password_hash
            user.hashed_password = generate_password_hash(password)

        db.session.commit()
        flash('User updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {str(e)}', 'danger')

    return redirect(url_for('admin.user_detail', user_id=user.id))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete a user and their associated wallet.
    """
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/products', methods=['GET'])
@login_required
@admin_required
def products():
    """
    Display all products.
    """
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    """
    Create a new product.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        category = request.form.get('category')

        if not name:
            flash("Product name is required.", "danger")
            return redirect(url_for('admin.create_product'))

        try:
            product = Product(
                name=name,
                description=description,
                image_url=image_url,
                category=category
            )
            db.session.add(product)
            db.session.commit()
            flash("Product created successfully.", "success")
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating product: {str(e)}", "danger")
            return redirect(url_for('admin.create_product'))

    return render_template('admin/create_product.html')

@admin_bp.route('/auctions', methods=['GET'])
@login_required
@admin_required
def auctions():
    """
    Display all auctions and products for creating new auctions.
    """
    auctions = Auction.query.all()
    products = Product.query.filter_by(is_active=True).all()  # Fetch only active products
    return render_template('admin/auctions.html', auctions=auctions, products=products)

@admin_bp.route('/auctions/create/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def create_auction(product_id):
    """
    Create a new auction for a specific product.
    """
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        starting_price = request.form.get('starting_price', type=float)
        start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')

        try:
            auction = Auction(
                product_id=product.id,
                product_name=product.name,
                product_description=product.description,
                product_price=starting_price,
                start_time=start_time,
                end_time=end_time,
                current_price=starting_price,
                is_active=True
            )
            db.session.add(auction)
            db.session.commit()
            flash('Auction created successfully!', 'success')
            return redirect(url_for('admin.auctions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating auction: {str(e)}', 'danger')

    return render_template('admin/create_auction.html', product=product)

@admin_bp.route('/auctions/<int:auction_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_auction(auction_id):
    """
    Delete an auction.
    """
    auction = Auction.query.get_or_404(auction_id)
    try:
        db.session.delete(auction)
        db.session.commit()
        flash('Auction deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting auction: {str(e)}', 'danger')
    return redirect(url_for('admin.auctions'))

@admin_bp.route('/auctions/<int:auction_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_auction(auction_id):
    """
    Edit an auction.
    """
    auction = Auction.query.get_or_404(auction_id)

    if request.method == 'POST':
        try:
            auction.product_id = request.form.get('product_id')
            auction.product_price = float(request.form.get('starting_price'))
            auction.token_cost_per_bid = int(request.form.get('token_cost_per_bid', 1))
            auction.start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
            auction.end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
            auction.status = request.form.get('status', auction.status)

            db.session.commit()
            flash('Enchère mise à jour avec succès!', 'success')
            return redirect(url_for('admin.auctions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour de l\'enchère: {str(e)}', 'danger')

    products = Product.query.all()
    return render_template('admin/edit_auction.html', auction=auction, products=products)
@admin_bp.route('/auctions/<int:auction_id>/bids', methods=['GET'])
@login_required
@admin_required
def view_bids(auction_id):
    """
    View all bids for a specific auction.
    """
    auction = Auction.query.get_or_404(auction_id)
    bids = auction.bids.order_by(Bid.amount.desc()).all()  # Order bids by amount (highest first)
    return render_template('admin/view_bids.html', auction=auction, bids=bids)

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """
    Edit a product.
    """
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.image_url = request.form.get('image_url')
            product.category = request.form.get('category')
            product.is_active = 'is_active' in request.form

            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')

    return render_template('admin/edit_product.html', product=product)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    """
    Delete a product.
    """
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')
    return redirect(url_for('admin.products'))

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def user_list():
    """
    Display all users.
    """
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

# Ajoutez ces routes à votre fichier admin.py existant

@admin_bp.route('/token-packs', methods=['GET'])
@login_required
@admin_required
def token_packs():
    """
    Gérer les packs de jetons.
    """
    packs = TokenPack.query.order_by(TokenPack.tokens).all()
    return render_template('admin/token_packs.html', packs=packs)

@admin_bp.route('/token-packs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_token_pack():
    """
    Créer un nouveau pack de jetons.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        tokens = int(request.form.get('tokens'))
        price = float(request.form.get('price'))
        discount_percentage = float(request.form.get('discount_percentage', 0))
        is_active = 'is_active' in request.form
        
        try:
            pack = TokenPack(
                name=name,
                tokens=tokens,
                price=price,
                discount_percentage=discount_percentage,
                is_active=is_active
            )
            
            db.session.add(pack)
            db.session.commit()
            flash('Pack de jetons créé avec succès!', 'success')
            return redirect(url_for('admin.token_packs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du pack: {str(e)}', 'danger')
    
    return render_template('admin/create_token_pack.html')

@admin_bp.route('/token-packs/<int:pack_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_token_pack(pack_id):
    """
    Modifier un pack de jetons.
    """
    pack = TokenPack.query.get_or_404(pack_id)
    
    if request.method == 'POST':
        pack.name = request.form.get('name')
        pack.tokens = int(request.form.get('tokens'))
        pack.price = float(request.form.get('price'))
        pack.discount_percentage = float(request.form.get('discount_percentage', 0))
        pack.is_active = 'is_active' in request.form
        
        try:
            db.session.commit()
            flash('Pack de jetons mis à jour avec succès!', 'success')
            return redirect(url_for('admin.token_packs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour du pack: {str(e)}', 'danger')
    
    return render_template('admin/edit_token_pack.html', pack=pack)

@admin_bp.route('/token-packs/<int:pack_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_token_pack(pack_id):
    """
    Supprimer un pack de jetons.
    """
    pack = TokenPack.query.get_or_404(pack_id)
    
    try:
        db.session.delete(pack)
        db.session.commit()
        flash('Pack de jetons supprimé avec succès!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'danger')
    
    return redirect(url_for('admin.token_packs'))