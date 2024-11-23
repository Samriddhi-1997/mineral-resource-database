from app import db

# Existing Mineral model
class Mineral(db.Model):
    __tablename__ = 'minerals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    location = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    reserve_size = db.Column(db.Float)
    grade = db.Column(db.Float)
    extraction_cost = db.Column(db.Float)
    applications = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'reserve_size': self.reserve_size,
            'grade': self.grade,
            'extraction_cost': self.extraction_cost,
            'applications': self.applications,
        }

# EnvironmentalMetric model
class EnvironmentalMetric(db.Model):
    __tablename__ = 'environmental_metrics'
    id = db.Column(db.Integer, primary_key=True)
    mineral_id = db.Column(db.Integer, db.ForeignKey('minerals.id'))
    carbon_emissions = db.Column(db.Float)
    water_usage = db.Column(db.Float)
    land_degradation = db.Column(db.Float)
    energy_consumption = db.Column(db.Float)
    rehabilitation_efforts = db.Column(db.Text)

    mineral = db.relationship('Mineral', backref=db.backref('metrics', lazy=True))

# New Mine model
class Mine(db.Model):
    __tablename__ = 'mines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    mineral_id = db.Column(db.Integer, db.ForeignKey('minerals.id'), nullable=False)

    # Relationship to the Mineral model
    mineral = db.relationship('Mineral', backref=db.backref('mines', lazy=True))

    def __repr__(self):
        return f'<Mine {self.name} in {self.state}>'

