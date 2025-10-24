import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///problemscope.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Pagination
    PROBLEMS_PER_PAGE = 6
    COMMENTS_PER_PAGE = 10
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Admin
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@problemscope.com'