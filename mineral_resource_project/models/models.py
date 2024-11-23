from app import db
from flask_login import UserMixin

class Mineral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    reserve_size = db.Column(db.Float, nullable=False)
    extraction_cost = db.Column(db.Float, nullable=False)
    carbon_emissions = db.Column(db.Float, nullable=True)
    water_usage = db.Column(db.Float, nullable=True)
    land_degradation = db.Column(db.Float, nullable=True)
    rehabilitation_efforts = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Mineral {self.name}>'
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'