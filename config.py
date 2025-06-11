import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration settings for the Flask application"""
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PostgreSQL connection pool settings for Gunicorn
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,  # Recycle connections every hour
        'pool_pre_ping': True,  # Validate connections before use
        'max_overflow': 20,
        'pool_timeout': 30,
        'echo': False  # Set to True for debugging SQL queries
    }
    
    # Debug mode (disable in production)
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    # Pagination settings
    STATUTES_PER_PAGE = 10
    ANNOTATIONS_PER_PAGE = 20
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Use environment variables for production settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Additional production-specific settings
    PREFERRED_URL_SCHEME = 'https'

# Map environment names to config classes
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Get configuration class based on environment variable, default to development
config_name = os.environ.get('FLASK_ENV', 'default')
Config = config_by_name[config_name]
print(f"Using {config_name} configuration")
print(f"Database URI: {Config.SQLALCHEMY_DATABASE_URI}")