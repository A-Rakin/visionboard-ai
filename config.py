import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'visionboard-ai-super-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'visionboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload & Storage Directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'uploads')
    EMBEDDING_FOLDER = os.path.join(BASE_DIR, 'app', 'embeddings')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'app', 'reports')
    
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max upload
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

    # Swagger API config
    SWAGGER = {
        'title': 'VisionBoard AI REST API',
        'uiversion': 3,
        'description': 'AI-Powered Visual Search & Image Intelligence Engine API',
        'version': '1.0.0'
    }

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.EMBEDDING_FOLDER, exist_ok=True)
        os.makedirs(Config.REPORT_FOLDER, exist_ok=True)

