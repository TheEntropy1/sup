import os

class Config:
    # Flask configuration
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'marlin_secret_key')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///marlin.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Mega.nz configuration
    MEGA_EMAIL = os.environ.get('MEGA_EMAIL')
    MEGA_PASSWORD = os.environ.get('MEGA_PASSWORD')
    
    # Thread cleanup configuration
    THREAD_MAX_AGE_DAYS = 120  # 4 months
    THREAD_CLEANUP_INTERVAL_HOURS = 24
    
    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Admin configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@marlin.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'marlinadmin')
