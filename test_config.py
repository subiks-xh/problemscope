from app import create_app

app = create_app()

with app.app_context():
    print("=" * 50)
    print("EMAIL CONFIGURATION CHECK")
    print("=" * 50)
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"MAIL_PASSWORD: {'*' * 10 if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
    print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
    print(f"ADMIN_EMAIL: {app.config.get('ADMIN_EMAIL')}")
    print("=" * 50)