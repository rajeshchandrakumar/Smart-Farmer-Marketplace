from datetime import datetime
from database import db

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', back_populates='feedbacks', lazy=True)
    buyer = db.relationship('Buyer', back_populates='feedbacks', lazy=True)
    
    def __repr__(self):
        return f'<Feedback {self.id} - Product {self.product_id} - Rating {self.rating}>'