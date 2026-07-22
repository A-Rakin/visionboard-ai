from datetime import datetime
from app.models import db

class SearchHistory(db.Model):
    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    query_text = db.Column(db.String(255), nullable=False)
    search_type = db.Column(db.String(50), default='text') # text, image, color, tag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query': self.query_text,
            'search_type': self.search_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

