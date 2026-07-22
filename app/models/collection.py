from datetime import datetime
from app.models import db

collection_images = db.Table('collection_images',
    db.Column('collection_id', db.Integer, db.ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), primary_key=True)
)

class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    collection_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('Image', secondary=collection_images, backref=db.backref('in_collections', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'collection_name': self.collection_name,
            'description': self.description,
            'image_count': self.images.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
