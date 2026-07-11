from datetime import datetime
from database import db

class Promotion(db.Model):
    __tablename__ = 'promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    discount_percent = db.Column(db.Float, nullable=False)  # e.g., 10.0 for 10% off
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', back_populates='promotions', lazy=True)
    
    def __repr__(self):
        return f'<Promotion {self.id} - {self.discount_percent}% off>'
    
    @property
    def is_active(self):
        """Check if promotion is currently active"""
        from datetime import datetime
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date