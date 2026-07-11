import os
from datetime import datetime, timedelta

def init_db():
    """Initialize the database with tables and sample data"""
    
    # Import here to avoid circular imports
    from app import app, db
    from models import User, Farmer, Buyer, Product, Order, OrderItem, Promotion, Feedback
    
    # Get the database path relative to the project directory
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")
    
    # Create database and tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
        # Create default admin user
        admin_user = User(
            name="Admin User",
            email="admin@smartfarmer.com",
            role="admin"
        )
        admin_user.set_password("admin123")  # Default admin password
        db.session.add(admin_user)
        db.session.commit()
        
        print("Admin user created: admin@smartfarmer.com / admin123")
        
        # Create sample farmers
        farmer1 = User(name="Rajesh Kumar", email="rajesh@example.com", role="farmer")
        farmer1.set_password("farmer123")
        db.session.add(farmer1)
        
        farmer2 = User(name="Priya Sharma", email="priya@example.com", role="farmer")
        farmer2.set_password("farmer123")
        db.session.add(farmer2)
        
        db.session.commit()
        
        # Create farmer profiles
        rajesh_farmer = Farmer(user_id=farmer1.id, farm_name="Green Fields Farm", location="Pune, Maharashtra", contact_number="+91-9876543210")
        priya_farmer = Farmer(user_id=farmer2.id, farm_name="Organic Harvest", location="Bangalore, Karnataka", contact_number="+91-9876543211")
        
        db.session.add(rajesh_farmer)
        db.session.add(priya_farmer)
        db.session.commit()
        
        print("Sample farmers created")
        
        # Create sample buyers
        buyer1 = User(name="Amit Patel", email="amit@example.com", role="buyer")
        buyer1.set_password("buyer123")
        db.session.add(buyer1)
        
        buyer2 = User(name="Sneha Reddy", email="sneha@example.com", role="buyer")
        buyer2.set_password("buyer123")
        db.session.add(buyer2)
        
        db.session.commit()
        
        # Create buyer profiles
        amit_buyer = Buyer(user_id=buyer1.id, contact_number="+91-9876543212")
        sneha_buyer = Buyer(user_id=buyer2.id, contact_number="+91-9876543213")
        
        db.session.add(amit_buyer)
        db.session.add(sneha_buyer)
        db.session.commit()
        
        print("Sample buyers created")
        
        # Create sample products
        product1 = Product(
            farmer_id=rajesh_farmer.id,
            name="Organic Tomatoes",
            description="Fresh organic tomatoes grown without pesticides",
            category="Vegetables",
            price=40.00,
            quantity=50,
            status="approved"
        )
        
        product2 = Product(
            farmer_id=rajesh_farmer.id,
            name="Farm Fresh Potatoes",
            description="Locally grown potatoes, perfect for cooking",
            category="Vegetables",
            price=30.00,
            quantity=100,
            status="approved"
        )
        
        product3 = Product(
            farmer_id=priya_farmer.id,
            name="Organic Spinach",
            description="Nutritious organic spinach leaves",
            category="Leafy Greens",
            price=25.00,
            quantity=30,
            status="approved"
        )
        
        product4 = Product(
            farmer_id=priya_farmer.id,
            name="Fresh Carrots",
            description="Sweet and crunchy carrots from our farm",
            category="Vegetables",
            price=35.00,
            quantity=40,
            status="approved"
        )
        
        db.session.add(product1)
        db.session.add(product2)
        db.session.add(product3)
        db.session.add(product4)
        db.session.commit()
        
        print("Sample products created")
        
        # Create sample orders
        order1 = Order(
            buyer_id=amit_buyer.id,
            total_amount=70.00,
            status="delivered"
        )
        db.session.add(order1)
        db.session.commit()
        
        # Add order items
        order_item1 = OrderItem(
            order_id=order1.id,
            product_id=product1.id,
            quantity=1,
            price=40.00
        )
        order_item2 = OrderItem(
            order_id=order1.id,
            product_id=product3.id,
            quantity=1,
            price=30.00
        )
        db.session.add(order_item1)
        db.session.add(order_item2)
        db.session.commit()
        
        print("Sample orders created")
        
        # Create sample promotions
        promo1 = Promotion(
            product_id=product1.id,
            discount_percent=10.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            description="Welcome discount on organic tomatoes"
        )
        db.session.add(promo1)
        db.session.commit()
        
        print("Sample promotions created")
        
        # Create sample feedback
        feedback1 = Feedback(
            product_id=product1.id,
            buyer_id=amit_buyer.id,
            rating=5,
            comment="Excellent quality tomatoes, very fresh!"
        )
        feedback2 = Feedback(
            product_id=product3.id,
            buyer_id=amit_buyer.id,
            rating=4,
            comment="Good spinach, will buy again"
        )
        db.session.add(feedback1)
        db.session.add(feedback2)
        db.session.commit()
        
        print("Sample feedback created")
        
        print("\nDatabase initialized successfully with sample data!")
        print(f"Database location: {db_path}")
        print("\nSample accounts:")
        print("- Admin: admin@smartfarmer.com / admin123")
        print("- Farmer: rajesh@example.com / farmer123")
        print("- Farmer: priya@example.com / farmer123")
        print("- Buyer: amit@example.com / buyer123")
        print("- Buyer: sneha@example.com / buyer123")

if __name__ == "__main__":
    init_db()