from datetime import datetime
from database import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', lazy=True)
    feedbacks = db.relationship('Feedback', back_populates='product', lazy=True)
    promotions = db.relationship('Promotion', back_populates='product', lazy=True)
    farmer = db.relationship('Farmer', back_populates='products', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def average_rating(self):
        """Calculate average rating from feedback"""
        if not self.feedbacks:
            return 0
        total_rating = sum(feedback.rating for feedback in self.feedbacks)
        return total_rating / len(self.feedbacks)