from app.models import db

class ExtractedText(db.Model):
    __tablename__ = 'extracted_text'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, default=1.0)
    language = db.Column(db.String(20), default='en')

    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'text': self.text,
            'confidence': round(self.confidence, 4),
            'language': self.language
        }
