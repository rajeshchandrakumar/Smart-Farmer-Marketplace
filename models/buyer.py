from datetime import datetime
from database import db

class Buyer(db.Model):
    __tablename__ = 'buyers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_number = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='buyer_profile')
    orders = db.relationship('Order', back_populates='buyer', lazy=True)
    feedbacks = db.relationship('Feedback', back_populates='buyer', lazy=True)
    
    def __repr__(self):
        return f'<Buyer {self.user.name}>'