# filepath: c:\Users\enzon\OneDrive\Desktop\Productivity\Classes\Web\auction_site\wsgi.py
from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run()