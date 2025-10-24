import os
import secrets
from PIL import Image
from flask import current_app
from app.models import Activity
from app import db

def save_picture(form_picture, folder='problems'):
    """Save uploaded picture and return filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, f'static/images/{folder}', picture_fn)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Resize image to save space
    output_size = (800, 600) if folder == 'problems' else (200, 200)
    img = Image.open(form_picture)
    
    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_fn


def log_activity(user_id, activity_type, description, problem_id=None):
    """Log user activity"""
    activity = Activity(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        problem_id=problem_id
    )
    db.session.add(activity)
    db.session.commit()


def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS