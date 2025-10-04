from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from os import path
from dotenv import load_dotenv

# Load environment variables (e.g., for SendGrid)
load_dotenv()

# Global variables
db = SQLAlchemy()
login_manager = LoginManager()
DB_NAME = "database.db"
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')


def create_app():
    app = Flask(__name__)

    # Basic config
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "gvfvsvf")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Optional: SendGrid config from .env
    # app.config['SENDGRID_API_KEY'] = os.getenv('SENDGRID_API_KEY')
    # app.config['SENDGRID_DEFAULT_SENDER'] = os.getenv('SENDGRID_DEFAULT_SENDER', 'you@example.com')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register Blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import models here to avoid circular imports
    from .models import User, Topic, Subtopic, LearningOutcome

    # Create the database if it doesn't exist
    create_database(app)

    # Setup user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def create_database(app):
    db_path = path.join('website', DB_NAME)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print("✅ Database created at", db_path)
