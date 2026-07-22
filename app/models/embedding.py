from datetime import datetime
from app.models import db

class ImageEmbedding(db.Model):
    __tablename__ = 'image_embeddings'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False, index=True)
    embedding_path = db.Column(db.String(512), nullable=False)
    model_name = db.Column(db.String(100), default='CLIP-ViT-B/32')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'embedding_path': self.embedding_path,
            'model_name': self.model_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
