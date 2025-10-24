from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@problemscope.com').first()
    print('Admin exists:', admin is not None)
    if admin:
        print('Username:', admin.username)
        print('Password hash:', admin.password)
        print('Is admin:', admin.is_admin)
        print('Is verified:', admin.is_verified)
    else:
        print('Admin not found in database')
