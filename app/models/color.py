from app.models import db

class DominantColor(db.Model):
    __tablename__ = 'dominant_colors'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False, index=True)
    hex_code = db.Column(db.String(10), nullable=False, index=True) # e.g. #0057FF
    rgb_value = db.Column(db.String(30), nullable=False) # e.g. rgb(0, 87, 255)
    percentage = db.Column(db.Float, nullable=False) # e.g. 45.2

    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'hex_code': self.hex_code,
            'rgb_value': self.rgb_value,
            'percentage': round(self.percentage, 2)
        }
