import os
from flask import Flask, render_template
from config import Config
from app.models import db, login_manager
try:
    from flasgger import Swagger
    HAS_FLASGGER = True
except ImportError:
    HAS_FLASGGER = False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    Config.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # Flasgger Swagger Docs if available
    if HAS_FLASGGER:
        Swagger(app)

    # Register Blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.upload.routes import upload_bp
    from app.api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(api_bp)

    @app.route('/apidocs')
    def swagger_docs_view():
        return render_template('apidocs.html')

    # Create DB tables and seed default user
    with app.app_context():
        db.create_all()
        seed_default_user()

    return app

def seed_default_user():
    from app.models.user import User
    if not User.query.filter_by(username='demo').first():
        demo_user = User(username='demo', email='demo@visionboard.ai')
        demo_user.set_password('demo1234')
        db.session.add(demo_user)
        db.session.commit()
        print("[Database Seed] Demo user created: username='demo', password='demo1234'")
