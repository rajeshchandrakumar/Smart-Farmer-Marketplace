#!/usr/bin/env python3
"""Database initialization script with sample data for Smart Farmer Marketplace"""

from app import create_app
from database import db
from models import User, Farmer, Buyer, Product, Order, OrderItem, Promotion, Feedback
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    app = create_app()
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Creating sample users...")
        
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@example.com",
            role="admin"
        )
        admin.password_hash = generate_password_hash("admin123")  # Using the setter
        db.session.add(admin)
        
        # Create sample farmers
        farmer1 = User(
            name="Rajesh Kumar",
            email="farmer1@example.com",
            role="farmer"
        )
        farmer1.password_hash = generate_password_hash("farmer123")
        db.session.add(farmer1)
        
        farmer2 = User(
            name="Priya Sharma",
            email="farmer2@example.com",
            role="farmer"
        )
        farmer2.password_hash = generate_password_hash("farmer123")
        db.session.add(farmer2)
        
        db.session.commit()  # Commit to get IDs
        
        # Create farmer profiles
        farmer_profile1 = Farmer(
            user_id=farmer1.id,
            farm_name="Green Valley Farms",
            location="Bangalore, Karnataka",
            contact_number="9876543210"
        )
        db.session.add(farmer_profile1)
        
        farmer_profile2 = Farmer(
            user_id=farmer2.id,
            farm_name="Organic Fields",
            location="Chennai, Tamil Nadu",
            contact_number="9123456789"
        )
        db.session.add(farmer_profile2)
        
        # Create sample buyers
        buyer1 = User(
            name="Suresh Patel",
            email="buyer1@example.com",
            role="buyer"
        )
        buyer1.password_hash = generate_password_hash("buyer123")
        db.session.add(buyer1)
        
        buyer2 = User(
            name="Anita Desai",
            email="buyer2@example.com",
            role="buyer"
        )
        buyer2.password_hash = generate_password_hash("buyer123")
        db.session.add(buyer2)
        
        db.session.commit()  # Commit to get IDs
        
        # Create buyer profiles
        buyer_profile1 = Buyer(
            user_id=buyer1.id,
            contact_number="9988776655"
        )
        db.session.add(buyer_profile1)
        
        buyer_profile2 = Buyer(
            user_id=buyer2.id,
            contact_number="9876543210"
        )
        db.session.add(buyer_profile2)
        
        db.session.commit()
        
        print("Creating sample products...")
        
        # Create sample products for farmer1
        products_farmer1 = [
            Product(
                name="Fresh Organic Tomatoes",
                description="Premium quality organic tomatoes, freshly harvested from our farm. Rich in vitamins and great for salads.",
                category="Vegetables",
                price=45.00,
                quantity=100,
                farmer_id=farmer_profile1.id,
                image_path=None,  # No image initially
                status='approved'  # Approved for immediate visibility
            ),
            Product(
                name="Alphonso Mangoes",
                description="Sweet and juicy Alphonso mangoes, hand-picked at perfect ripeness. Known as the king of mangoes.",
                category="Fruits",
                price=120.00,
                quantity=50,
                farmer_id=farmer_profile1.id,
                image_path=None,  # No image initially
                status='approved'
            ),
            Product(
                name="Purple Carrots",
                description="Nutrient-rich purple carrots with antioxidant properties. Fresh from the farm to your table.",
                category="Vegetables",
                price=30.00,
                quantity=75,
                farmer_id=farmer_profile1.id,
                image_path=None,  # No image initially
                status='approved'
            )
        ]
        
        # Create sample products for farmer2
        products_farmer2 = [
            Product(
                name="Himachal Apples",
                description="Crisp and sweet apples grown in the hills of Himachal Pradesh. Perfect for snacking.",
                category="Fruits",
                price=80.00,
                quantity=60,
                farmer_id=farmer_profile2.id,
                image_path=None,  # No image initially
                status='approved'
            ),
            Product(
                name="Coorg Coffee Beans",
                description="Premium Arabica coffee beans from the hills of Coorg. Rich aroma and flavor.",
                category="Other",
                price=350.00,
                quantity=25,
                farmer_id=farmer_profile2.id,
                image_path=None,  # No image initially
                status='approved'
            ),
            Product(
                name="Coconut Oil",
                description="Cold-pressed virgin coconut oil, extracted from fresh coconuts. Pure and chemical-free.",
                category="Other",
                price=180.00,
                quantity=40,
                farmer_id=farmer_profile2.id,
                image_path=None,  # No image initially
                status='approved'
            )
        ]
        
        # Add all products to session
        for product in products_farmer1 + products_farmer2:
            db.session.add(product)
        
        db.session.commit()
        
        print("Creating sample orders...")
        
        # Create sample orders
        order1 = Order(
            buyer_id=buyer_profile1.id,
            total_amount=210.00,  # 1 tomato pack + 1 apple pack
            status='delivered'
        )
        db.session.add(order1)
        
        order2 = Order(
            buyer_id=buyer_profile2.id,
            total_amount=120.00,  # 1 mango pack
            status='confirmed'
        )
        db.session.add(order2)
        
        db.session.commit()
        
        # Create order items
        # Order 1 items
        order_item1 = OrderItem(
            order_id=order1.id,
            product_id=products_farmer1[0].id,  # Tomatoes
            quantity=1,
            price=products_farmer1[0].price
        )
        db.session.add(order_item1)
        
        order_item2 = OrderItem(
            order_id=order1.id,
            product_id=products_farmer2[0].id,  # Apples
            quantity=1,
            price=products_farmer2[0].price
        )
        db.session.add(order_item2)
        
        # Order 2 items
        order_item3 = OrderItem(
            order_id=order2.id,
            product_id=products_farmer1[1].id,  # Mangoes
            quantity=1,
            price=products_farmer1[1].price
        )
        db.session.add(order_item3)
        
        db.session.commit()
        
        print("Creating sample promotions...")
        
        # Create sample promotions
        promo1 = Promotion(
            description="Special discount on summer fruits",
            discount_percent=15.0,
            start_date=datetime.strptime("2024-06-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-08-31", "%Y-%m-%d").date(),
            product_id=products_farmer1[1].id,  # Mangoes
        )
        db.session.add(promo1)
        
        promo2 = Promotion(
            description="10% off on all organic vegetables",
            discount_percent=10.0,
            start_date=datetime.strptime("2024-01-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-12-31", "%Y-%m-%d").date(),
            product_id=products_farmer1[0].id,  # Tomatoes
        )
        db.session.add(promo2)
        
        db.session.commit()
        
        print("Creating sample feedback...")
        
        # Create sample feedback
        feedback1 = Feedback(
            product_id=products_farmer1[1].id,  # Mangoes
            buyer_id=buyer_profile1.id,
            rating=5,
            comment="Excellent quality mangoes! Very sweet and fresh."
        )
        db.session.add(feedback1)
        
        feedback2 = Feedback(
            product_id=products_farmer1[0].id,  # Tomatoes
            buyer_id=buyer_profile2.id,
            rating=4,
            comment="Good quality tomatoes, will buy again."
        )
        db.session.add(feedback2)
        
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nSample Accounts:")
        print("- Admin: admin@example.com / admin123")
        print("- Farmer: farmer1@example.com / farmer123")
        print("- Farmer: farmer2@example.com / farmer123")
        print("- Buyer: buyer1@example.com / buyer123")
        print("- Buyer: buyer2@example.com / buyer123")

if __name__ == "__main__":
    init_database()