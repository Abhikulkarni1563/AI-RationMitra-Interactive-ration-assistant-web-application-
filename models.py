from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------- User Table --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    aadhar = db.Column(db.String(12), unique=True, nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    
    # Relationships
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    rations = db.relationship('UserRation', backref='user', lazy=True)

# -------------------- Admin Table --------------------
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# -------------------- Commodity Table --------------------
class Commodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    
    # Optional: Future use for pricing, unit, etc.
    unit = db.Column(db.String(20), default='kg')  # kg/liters etc.
    price_per_unit = db.Column(db.Float, default=0.0)

    # Relationship
    user_quotas = db.relationship('UserRation', backref='commodity_obj', lazy=True, cascade='all, delete')

# -------------------- User Ration Quota Table --------------------
class UserRation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'), nullable=False)
    
    quota_limit = db.Column(db.Integer, nullable=False)  # Monthly quota
    consumed = db.Column(db.Integer, default=0)          # Already consumed
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'commodity_id', name='user_commodity_uc'),
    )

# -------------------- Feedback Table --------------------

from extensions import db
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)




# -------------------- Government Scheme Table --------------------
class GovtScheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scheme_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    launch_date = db.Column(db.Date, nullable=True)
    eligibility = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    state = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    source_url = db.Column(db.String(255), nullable=True)
