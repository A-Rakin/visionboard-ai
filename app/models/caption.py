from datetime import datetime
from app.models import db

class Caption(db.Model):
    __tablename__ = 'captions'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False, index=True)
    generated_caption = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'generated_caption': self.generated_caption,
            'confidence': round(self.confidence, 4),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
