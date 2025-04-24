from datetime import datetime
from flask import current_app
from models import db
from models.auction import Auction

def check_finished_auctions(app):
    """
    Check for finished auctions and process them.
    """
    with app.app_context():
        # Fetch all active auctions that have ended
        finished_auctions = Auction.query.filter(
            Auction.is_active == True,
            Auction.end_time <= datetime.utcnow()
        ).all()

        for auction in finished_auctions:
            try:
                # Mark the auction as inactive
                auction.is_active = False
                auction.status = 'completed'

                # Refund non-winning bidders
                auction.refund_non_winning_bidders()

                # Log the winner
                winner = auction.get_winner()
                if winner:
                    current_app.logger.info(f"Enchère {auction.id} terminée. Gagnant: {winner.username} avec l'enchère unique la plus basse")
                else:
                    current_app.logger.info(f"Enchère {auction.id} terminée sans gagnant (pas d'enchère unique).")

            except Exception as e:
                current_app.logger.error(f"Erreur lors du traitement de l'enchère {auction.id}: {str(e)}")

        # Commit all changes to the database
        db.session.commit()