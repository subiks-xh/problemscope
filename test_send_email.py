from app import create_app, mail
from flask_mail import Message
import sys

app = create_app()

with app.app_context():
    try:
        print("\n" + "=" * 60)
        print("TESTING EMAIL SENDING")
        print("=" * 60)
        
        # Print configuration
        print(f"\n📧 Configuration:")
        print(f"   Server: {app.config['MAIL_SERVER']}")
        print(f"   Port: {app.config['MAIL_PORT']}")
        print(f"   TLS: {app.config['MAIL_USE_TLS']}")
        print(f"   Username: {app.config['MAIL_USERNAME']}")
        print(f"   From: {app.config['MAIL_DEFAULT_SENDER']}")
        
        # Ask for recipient
        print(f"\n📬 Sending test email...")
        recipient = input("Enter recipient email (or press Enter to use sender email): ").strip()
        
        if not recipient:
            recipient = app.config['MAIL_USERNAME']
        
        print(f"   To: {recipient}")
        
        # Create test message
        msg = Message(
            subject='🧪 Test Email from ProblemScope',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[recipient]
        )
        
        msg.body = '''
Hello!

This is a test email from your ProblemScope application.

If you receive this, your email configuration is working correctly! ✅

Test Details:
- Server: {server}
- Port: {port}
- From: {sender}
- To: {recipient}

Best regards,
ProblemScope System
        '''.format(
            server=app.config['MAIL_SERVER'],
            port=app.config['MAIL_PORT'],
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipient=recipient
        )
        
        msg.html = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c3e50;">🧪 Test Email from ProblemScope</h2>
            <p>Hello!</p>
            <p>This is a test email from your ProblemScope application.</p>
            <div style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                <strong>✅ If you receive this, your email configuration is working correctly!</strong>
            </div>
            <h3>Test Details:</h3>
            <ul>
                <li><strong>Server:</strong> {app.config['MAIL_SERVER']}</li>
                <li><strong>Port:</strong> {app.config['MAIL_PORT']}</li>
                <li><strong>From:</strong> {app.config['MAIL_DEFAULT_SENDER']}</li>
                <li><strong>To:</strong> {recipient}</li>
            </ul>
            <p>Best regards,<br>ProblemScope System</p>
        </body>
        </html>
        '''
        
        print(f"\n📤 Sending email...")
        mail.send(msg)
        
        print("\n" + "=" * 60)
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n📥 Check your inbox: {recipient}")
        print("   Also check SPAM/JUNK folder!")
        print("\n")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ EMAIL SENDING FAILED!")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print(f"Type: {type(e).__name__}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING STEPS:")
        print("=" * 60)
        
        error_msg = str(e).lower()
        
        if 'username and password not accepted' in error_msg or '535' in error_msg:
            print("""
❌ Authentication Failed!

Solutions:
1. Make sure you're using App Password, NOT regular Gmail password
2. Generate new App Password:
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Go to App Passwords
   - Generate new password for "Mail"
   - Copy the 16-character password (no spaces!)
   
3. Update your .env or config.py with the App Password
            """)
        
        elif 'connection refused' in error_msg or 'connection' in error_msg:
            print("""
❌ Connection Failed!

Solutions:
1. Check your internet connection
2. Try different SMTP settings:
   
   Option 1 - Gmail with SSL:
   MAIL_SERVER = 'smtp.gmail.com'
   MAIL_PORT = 465
   MAIL_USE_SSL = True
   MAIL_USE_TLS = False
   
   Option 2 - Check firewall/antivirus
   - Disable firewall temporarily
   - Check if antivirus blocks SMTP
            """)
        
        elif 'timeout' in error_msg:
            print("""
❌ Timeout Error!

Solutions:
1. Check internet connection
2. Try port 465 instead of 587
3. Check if ISP blocks SMTP
            """)
        
        else:
            print("""
❌ Unknown Error!

General troubleshooting:
1. Verify Gmail credentials are correct
2. Check .env file exists and is loaded
3. Try hardcoding credentials in config.py temporarily
4. Check Gmail account settings allow "Less secure app access"
5. Try different email provider (Outlook, Yahoo)
            """)
        
        sys.exit(1)