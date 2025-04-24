import os

from flask import Flask, render_template, redirect, url_for, flash
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

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction_site.db'))
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auction_bp)
    app.register_blueprint(token_bp)
    
    # Migrate database
    migrate = Migrate(app, db)
    
    # Setup scheduler for checking finished auctions
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_finished_auctions, args=[app], trigger="interval", minutes=5)
    scheduler.start()
    
    @app.route('/')
    def home():
        active_auctions = Auction.query.filter(
            Auction.status == 'active',
            Auction.end_time > datetime.utcnow()  # Use end_time instead of buy_date
        ).order_by(Auction.end_time).limit(5).all()

        completed_auctions = Auction.query.filter(
            Auction.end_time <= datetime.utcnow()  # Use end_time instead of buy_date
        ).order_by(Auction.end_time.desc()).limit(5).all()

        # Add winner information to completed auctions
        completed_auctions_with_winners = []
        for auction in completed_auctions:
            winner = auction.get_winner()
            completed_auctions_with_winners.append({
                'auction': auction,
                'winner': winner
            })

        return render_template('home.html', 
                            active_auctions=active_auctions,
                            completed_auctions=completed_auctions_with_winners,
                            now=datetime.utcnow())
        
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
    app.run(debug=True)