from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@problemscope.com').first()
    
    if not admin:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(
            username='admin',
            email='admin@problemscope.com',
            password=hashed_password,
            location='System',
            skills='Platform Management',
            is_admin=True,
            is_verified=True,
            reputation_points=1000
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created!")
        print("📧 Email: admin@problemscope.com")
        print("🔑 Password: admin123")
    else:
        print("⚠️ Admin already exists!")