from app.models import db

class DetectedObject(db.Model):
    __tablename__ = 'detected_objects'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False, index=True)
    object_name = db.Column(db.String(100), nullable=False, index=True)
    confidence = db.Column(db.Float, nullable=False)
    x = db.Column(db.Float, nullable=False)       # Normalized bounding box top-left X (0.0 - 1.0)
    y = db.Column(db.Float, nullable=False)       # Normalized bounding box top-left Y (0.0 - 1.0)
    width = db.Column(db.Float, nullable=False)   # Normalized width (0.0 - 1.0)
    height = db.Column(db.Float, nullable=False)  # Normalized height (0.0 - 1.0)

    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'object_name': self.object_name,
            'confidence': round(self.confidence, 4),
            'box': {
                'x': self.x,
                'y': self.y,
                'width': self.width,
                'height': self.height
            }
        }
