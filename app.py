import os
import atexit
import threading

from flask import Flask, render_template, redirect, url_for, flash, request, Blueprint
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from models import db
from models.user import User
from models.wallet import Wallet
from models.product import Product
from models.auction import Auction
from models.bid import Bid
from models.token_pack import TokenPack
from models.token_purchase import TokenPurchase

# Import routes
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.auction import auction_bp
from routes.token import token_bp

# Import tasks
from tasks.auction_task import check_finished_auctions

# Create main blueprint - define it at the module level to ensure it exists
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Get current datetime
    now = datetime.utcnow()
    
    # Get all active auctions for the product grid
    all_active_auctions = Auction.query.filter_by(
        status='active', 
        is_active=True
    ).order_by(Auction.current_price.asc()).all()
    
    # Get unique categories for filtering
    categories = db.session.query(Product.category).filter(Product.category != None).distinct().order_by(Product.category).all()
    categories = [category[0] for category in categories]
    
    return render_template(
        'home.html',
        now=now,
        all_active_auctions=all_active_auctions,
        categories=categories
    )

# Scheduler instance defined at module level
scheduler = BackgroundScheduler()
scheduler_lock = threading.Lock()  # Lock to prevent concurrent scheduler initialization

def initialize_scheduler_with_app(app):
    """Initialize the scheduler with app context"""
    global scheduler
    
    with scheduler_lock:
        if not scheduler.running:
            with app.app_context():
                scheduler.add_job(
                    func=check_finished_auctions, 
                    args=[app], 
                    trigger="interval", 
                    minutes=5,
                    id='check_auctions',
                    replace_existing=True
                )
                scheduler.start()
                print("Scheduler started successfully")
                
                # Register shutdown
                atexit.register(lambda: scheduler.shutdown(wait=False))

def create_app():
    app = Flask(__name__)
    
    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction_site.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Secret key for session management
    app.secret_key = os.environ.get('SECRET_KEY', 'development_key')
    
    # Initialize database
    db.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Setup Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auction_bp)
    app.register_blueprint(token_bp)
    app.register_blueprint(main_bp)  # Register the main blueprint
    
    # Setup database migrations
    migrate = Migrate(app, db)
    
    # Modern replacement for before_first_request
    @app.route('/initialize-scheduler')
    def init_scheduler_route():
        initialize_scheduler_with_app(app)
        return "Scheduler initialized"
    
    # Instead of using before_first_request, use a regular route and then redirect
    @app.before_request
    def init_scheduler_before_request():
        if not scheduler.running and request.endpoint != 'init_scheduler_route':
            initialize_scheduler_with_app(app)
    
    @app.context_processor
    def inject_user_wallet():
        if current_user.is_authenticated:
            wallet = Wallet.query.filter_by(user_id=current_user.id).first()
            return {'user_wallet': wallet}
        return {'user_wallet': None}
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Initialize scheduler when the app starts
    with app.app_context():
        if not scheduler.running:
            initialize_scheduler_with_app(app)
    app.run(debug=True)