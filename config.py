import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = 'problemscope-secret-key-2024'
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'problemscope.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ==========================================
    # EMAIL CONFIGURATION - HARDCODED
    # REPLACE THESE WITH YOUR ACTUAL DETAILS!
    # ==========================================
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # ⬇️⬇️⬇️ CHANGE THESE 4 LINES! ⬇️⬇️⬇️
    MAIL_USERNAME = '2312501@nec.edu.in'           # Your Gmail address
    MAIL_PASSWORD = 'vymlqpyataumwyzp'      # Your App Password (NO SPACES!)
    MAIL_DEFAULT_SENDER = '2312501@nec.edu.in'     # Same as MAIL_USERNAME
    ADMIN_EMAIL = '2312501@nec.edu.in'             # Same as MAIL_USERNAME
    # ⬆️⬆️⬆️ CHANGE THESE 4 LINES! ⬆️⬆️⬆️
    
    # Pagination
    PROBLEMS_PER_PAGE = 6
    COMMENTS_PER_PAGE = 10
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}