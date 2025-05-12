import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
scheduler = BackgroundScheduler()

# Create the app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Load configuration
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "marlin_secret_key")

# Initialize database
db.init_app(app)

# Setup login manager
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

with app.app_context():
    # Import models
    from models import User, Board, Thread, Post, Image
    
    # Create database tables
    db.create_all()
    
    # Import views and register blueprints
    from auth import auth_bp
    from boards import boards_bp
    from threads import threads_bp
    from admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(boards_bp)
    app.register_blueprint(threads_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Import and start tasks
    from tasks import start_scheduler
    start_scheduler(scheduler)
    
    # Create default boards if they don't exist
    from boards import create_default_boards
    create_default_boards()
    
    # Create admin user if it doesn't exist
    from auth import create_admin_user
    create_admin_user()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Root route redirects to boards
@app.route('/')
def index():
    from flask import redirect, url_for
    return redirect(url_for('boards.index'))
