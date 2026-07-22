from datetime import datetime
from app.models import db
from app.models.tag import image_tags

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    image_name = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    image_width = db.Column(db.Integer, default=0)
    image_height = db.Column(db.Integer, default=0)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processing_status = db.Column(db.String(50), default='completed') # pending, processing, completed, failed
    quality_score = db.Column(db.Float, default=0.0) # Blur/sharpness/brightness score (0-100)
    is_duplicate = db.Column(db.Boolean, default=False)
    is_favorite = db.Column(db.Boolean, default=False)
    exif_data = db.Column(db.Text, nullable=True) # JSON string of EXIF camera metadata

    # Relationships
    captions = db.relationship('Caption', backref='image', lazy=True, cascade='all, delete-orphan')
    objects = db.relationship('DetectedObject', backref='image', lazy=True, cascade='all, delete-orphan')
    texts = db.relationship('ExtractedText', backref='image', lazy=True, cascade='all, delete-orphan')
    colors = db.relationship('DominantColor', backref='image', lazy=True, cascade='all, delete-orphan')
    embedding = db.relationship('ImageEmbedding', backref='image', uselist=False, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=image_tags, backref=db.backref('images', lazy='dynamic'))

    def to_dict(self, include_details=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'image_name': self.image_name,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'processing_status': self.processing_status,
            'quality_score': self.quality_score,
            'is_duplicate': self.is_duplicate,
            'is_favorite': self.is_favorite
        }
        if include_details:
            data['caption'] = self.captions[0].generated_caption if self.captions else ''
            data['objects'] = [obj.to_dict() for obj in self.objects]
            data['ocr_text'] = [t.to_dict() for t in self.texts]
            data['colors'] = [c.to_dict() for c in self.colors]
            data['tags'] = [t.tag_name for t in self.tags]
        return data
