import os
import sys
from datetime import datetime
from flask import Flask
from models import db
from models.product import Product

def create_app():
    app = Flask(__name__)
    # Use an absolute path to ensure no permission issues
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auction_site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def seed_products():
    # Delete existing products to avoid duplicates
    Product.query.delete()
    
    # List of tech products with details
    products = [
        # Computers and Laptops
        {
            "name": "MacBook Pro 16-inch (2023)",
            "description": "Apple M2 Pro chip, 16GB RAM, 512GB SSD, 16-inch Liquid Retina XDR display",
            "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8bWFjYm9va3xlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Laptops"
        },
        {
            "name": "Dell XPS 15",
            "description": "Intel Core i7, 16GB RAM, 1TB SSD, NVIDIA GeForce RTX 3050 Ti, 15.6-inch 4K OLED",
            "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8ZGVsbCUyMGxhcHRvcHxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Laptops"
        },
        {
            "name": "HP Spectre x360",
            "description": "Intel Core i7, 16GB RAM, 1TB SSD, 13.5-inch 3K2K OLED touch display, convertible design",
            "image_url": "https://images.unsplash.com/photo-1587614313085-5da51cebd8ac?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8aHAlMjBsYXB0b3B8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Laptops"
        },
        {
            "name": "ASUS ROG Zephyrus G14",
            "description": "AMD Ryzen 9, 32GB RAM, 1TB SSD, NVIDIA GeForce RTX 4090, 14-inch QHD 165Hz display",
            "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTh8fGdhbWluZyUyMGxhcHRvcHxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Gaming Laptops"
        },
        {
            "name": "Microsoft Surface Laptop 5",
            "description": "Intel Core i7, 16GB RAM, 512GB SSD, 13.5-inch PixelSense touch display",
            "image_url": "https://images.unsplash.com/photo-1600267204091-5c1ab8b10c02?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8c3VyZmFjZSUyMGxhcHRvcHxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Laptops"
        },
        
        # Custom Desktop PCs
        {
            "name": "Ultimate Gaming PC",
            "description": "AMD Ryzen 9 7950X, NVIDIA RTX 4090, 64GB DDR5 RAM, 2TB NVMe SSD, custom liquid cooling",
            "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Nnx8Z2FtaW5nJTIwcGN8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Desktop PCs"
        },
        {
            "name": "Professional Workstation",
            "description": "Intel Core i9-13900K, NVIDIA RTX A5000, 128GB RAM, 4TB SSD, designed for creative professionals",
            "image_url": "https://images.unsplash.com/photo-1547082299-de196ea013d6?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTB8fHdvcmtzdGF0aW9ufGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Desktop PCs"
        },
        
        # Gaming Consoles
        {
            "name": "PlayStation 5",
            "description": "Sony's next-gen gaming console with ultra-high-speed SSD, 4K gaming, ray tracing, and DualSense controller",
            "image_url": "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8cGxheXN0YXRpb24lMjA1fGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Gaming Consoles"
        },
        {
            "name": "Xbox Series X",
            "description": "Microsoft's powerful console featuring 12 teraflops of processing power, 4K gaming at up to 120fps, and Quick Resume",
            "image_url": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8eGJveCUyMHNlcmllcyUyMHh8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Gaming Consoles"
        },
        {
            "name": "Nintendo Switch OLED",
            "description": "Enhanced handheld console with vibrant 7-inch OLED screen, enhanced audio, and wired LAN port",
            "image_url": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Nnx8bmludGVuZG8lMjBzd2l0Y2h8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Gaming Consoles"
        },
        
        # Smartphones
        {
            "name": "iPhone 14 Pro Max",
            "description": "A16 Bionic chip, 6.7-inch Super Retina XDR display with ProMotion, 48MP camera system, Dynamic Island",
            "image_url": "https://images.unsplash.com/photo-1663499482523-1c0c1bae4ce1?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTJ8fGlwaG9uZSUyMDE0fGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Smartphones"
        },
        {
            "name": "Samsung Galaxy S23 Ultra",
            "description": "Snapdragon 8 Gen 2, 6.8-inch Dynamic AMOLED 2X, 200MP camera, S Pen support, 5000mAh battery",
            "image_url": "https://images.unsplash.com/photo-1678911772950-fa2c88cf5634?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTV8fGdhbGF4eSUyMHMyM3xlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Smartphones"
        },
        {
            "name": "Google Pixel 7 Pro",
            "description": "Google Tensor G2 chip, 6.7-inch QHD+ LTPO OLED display, 50MP triple camera system with enhanced computational photography",
            "image_url": "https://images.unsplash.com/photo-1666863899729-e5f6fccb4f49?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8cGl4ZWwlMjA3fGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Smartphones"
        },
        
        # Audio Products
        {
            "name": "Sony WH-1000XM5",
            "description": "Premium noise-cancelling headphones with 30-hour battery life, LDAC support, and advanced audio processing",
            "image_url": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NHx8c29ueSUyMGhlYWRwaG9uZXN8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Audio"
        },
        {
            "name": "Apple AirPods Pro 2",
            "description": "Wireless earbuds with active noise cancellation, spatial audio, H2 chip, and MagSafe charging case",
            "image_url": "https://images.unsplash.com/photo-1588423771073-b8903fbb85b5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8YWlycG9kc3xlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Audio"
        },
        {
            "name": "Sonos Arc",
            "description": "Premium smart soundbar with Dolby Atmos, voice assistant support, and multi-room audio capability",
            "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8c291bmRiYXJ8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Audio"
        },
        
        # Smart Home
        {
            "name": "Amazon Echo Show 10",
            "description": "Smart display with 10.1-inch HD screen, rotating display, 13MP camera, and Alexa integration",
            "image_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8ZWNobyUyMHNob3d8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Smart Home"
        },
        {
            "name": "Philips Hue Starter Kit",
            "description": "Smart lighting system with bridge and 4 color-changing bulbs, compatible with various voice assistants",
            "image_url": "https://images.unsplash.com/photo-1558346490-a72e53ae2d4f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NHx8c21hcnQlMjBsaWdodHxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Smart Home"
        },
        {
            "name": "Ring Video Doorbell Pro 2",
            "description": "Advanced video doorbell with head-to-toe HD+ video, 3D motion detection, and two-way talk",
            "image_url": "https://images.unsplash.com/photo-1558346490-a72e53ae2d4f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NHx8c21hcnQlMjBsaWdodHxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Smart Home"
        },
        
        # Cameras
        {
            "name": "Canon EOS R5",
            "description": "45MP full-frame mirrorless camera with 8K video recording, in-body image stabilization, and RF mount",
            "image_url": "https://images.unsplash.com/photo-1516724562728-afc824a36e84?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8Y2Fub24lMjBjYW1lcmF8ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Cameras"
        },
        {
            "name": "Sony Alpha a7 IV",
            "description": "33MP full-frame mirrorless camera with 4K60p video, advanced autofocus, and excellent low-light performance",
            "image_url": "https://images.unsplash.com/photo-1617611653836-3f8cc69a1836?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8c29ueSUyMGNhbWVyYXxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60",
            "category": "Cameras"
        },
        {
            "name": "GoPro HERO11 Black",
            "description": "Rugged action camera with 5.3K video, HyperSmooth 5.0 stabilization, and waterproof design",
            "image_url": "https://images.unsplash.com/photo-1525385444278-b7968ccb841b?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8Z29wcm98ZW58MHx8MHx8&auto=format&fit=crop&w=500&q=60",
            "category": "Cameras"
        }
    ]
    
    # Add all products to database
    for product_data in products:
        product = Product(
            name=product_data["name"],
            description=product_data["description"],
            image_url=product_data["image_url"],
            category=product_data["category"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(product)
    
    # Commit changes
    db.session.commit()
    print(f"Successfully added {len(products)} products to the database.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_products()