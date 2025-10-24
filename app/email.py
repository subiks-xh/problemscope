from flask_mail import Message
from app import mail
from flask import current_app, render_template
from threading import Thread
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            print("      🔄 Async email send started...")
            mail.send(msg)
            print("      ✅ Async email send completed!")
            logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"      ❌ Async email send failed: {str(e)}")
            logger.error(f"Failed to send email: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

def send_email(subject, recipients, text_body, html_body):
    """Send email with detailed logging"""
    try:
        print("\n   --- send_email function called ---")
        print(f"   Subject: {subject}")
        print(f"   Recipients: {recipients}")
        
        msg = Message(subject, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        
        print(f"   Message object created")
        print(f"      From: {current_app.config['MAIL_DEFAULT_SENDER']}")
        print(f"      To: {recipients}")
        
        # Log email configuration
        print(f"\n   📧 Email Configuration:")
        print(f"      Server: {current_app.config['MAIL_SERVER']}")
        print(f"      Port: {current_app.config['MAIL_PORT']}")
        print(f"      TLS: {current_app.config['MAIL_USE_TLS']}")
        print(f"      Username: {current_app.config['MAIL_USERNAME']}")
        print(f"      Password: {'SET' if current_app.config['MAIL_PASSWORD'] else 'NOT SET'}")
        
        # Send SYNCHRONOUSLY for debugging (easier to catch errors)
        print(f"\n   📤 Sending email SYNCHRONOUSLY...")
        try:
            with current_app.app_context():
                mail.send(msg)
            
            print(f"   ✅ Email sent successfully!")
            logger.info(f"Email sent successfully to {recipients}")
            print("   --- send_email function finished (SUCCESS) ---\n")
            return True
            
        except Exception as send_error:
            print(f"   ❌ Email send failed!")
            print(f"      Error: {send_error}")
            import traceback
            traceback.print_exc()
            raise
        
    except Exception as e:
        print(f"\n   ❌ Exception in send_email:")
        print(f"      Type: {type(e).__name__}")
        print(f"      Message: {str(e)}")
        
        import traceback
        print("\n   Full traceback:")
        traceback.print_exc()
        
        logger.error(f"Email error: {str(e)}")
        print("   --- send_email function finished (ERROR) ---\n")
        return False


def send_verification_email(user, token):
    """Send email verification"""
    try:
        print("\n--- send_verification_email function called ---")
        print(f"User: {user.username}, Email: {user.email}")
        
        subject = 'Verify Your Email - ProblemScope'
        text_body = f'''
Hi {user.username},

Please verify your email by clicking this link:
http://127.0.0.1:5000/verify_email/{token}

This link expires in 1 hour.

Best regards,
ProblemScope Team
'''
        
        try:
            html_body = render_template('email/verify_email.html', user=user, token=token)
            print("✅ HTML template rendered")
        except Exception as e:
            print(f"⚠️ Template error: {e}, using text-only")
            html_body = f"<html><body><pre>{text_body}</pre></body></html>"
        
        result = send_email(subject, [user.email], text_body, html_body)
        
        if result:
            print(f"✅ Verification email sent to {user.email}")
        else:
            print(f"❌ Verification email failed")
        
        print("--- send_verification_email finished ---\n")
        return result
        
    except Exception as e:
        print(f"❌ Exception in send_verification_email: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Verification email error: {str(e)}")
        return False


def send_password_reset_email(user, token):
    """Send password reset email with detailed logging"""
    try:
        print("\n--- send_password_reset_email function called ---")
        print(f"📧 User: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"📧 Token (first 50 chars): {token[:50]}...")
        
        subject = 'Password Reset Request - ProblemScope'
        
        print("📝 Creating email body...")
        text_body = f'''
Hi {user.username},

To reset your password, click this link:
http://127.0.0.1:5000/reset_password/{token}

If you didn't request this, ignore this email.

This link expires in 30 minutes.

Best regards,
ProblemScope Team
'''
        
        print("📝 Rendering HTML template...")
        try:
            html_body = render_template('email/reset_password.html', user=user, token=token)
            print("   ✅ HTML template rendered successfully")
        except Exception as template_error:
            print(f"   ⚠️ Template error: {template_error}")
            print("   Using simple HTML instead")
            html_body = f'''
            <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2>Password Reset Request</h2>
                <p>Hi {user.username},</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="http://127.0.0.1:5000/reset_password/{token}" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a></p>
                <p>Or copy this link: http://127.0.0.1:5000/reset_password/{token}</p>
                <p style="color: #e74c3c;">If you didn't request this, ignore this email.</p>
                <p style="color: #95a5a6; font-size: 12px;">This link expires in 30 minutes.</p>
            </body>
            </html>
            '''
        
        print(f"📤 Calling send_email function...")
        result = send_email(subject, [user.email], text_body, html_body)
        
        if result:
            print(f"✅✅✅ Password reset email SENT to {user.email} ✅✅✅")
            logger.info(f"Password reset email sent to {user.email}")
        else:
            print(f"❌❌❌ Password reset email FAILED ❌❌❌")
        
        print("--- send_password_reset_email finished ---\n")
        return result
        
    except Exception as e:
        print(f"\n❌ Exception in send_password_reset_email:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        
        import traceback
        print("\n   Full traceback:")
        traceback.print_exc()
        
        logger.error(f"Password reset email error: {str(e)}")
        return False


def send_comment_notification(problem, comment):
    """Send notification for new comment"""
    if not problem.author.email_notifications:
        return False
        
    try:
        subject = f'New Comment on Your Problem - {problem.title}'
        text_body = f'''
Hi {problem.author.username},

{comment.author.username} commented on your problem "{problem.title}":

{comment.content}

View problem: http://127.0.0.1:5000/problem/{problem.id}

Best regards,
ProblemScope Team
'''
        
        try:
            html_body = render_template('email/comment_notification.html', 
                                       problem=problem, comment=comment)
        except:
            html_body = f"<html><body><pre>{text_body}</pre></body></html>"
        
        result = send_email(subject, [problem.author.email], text_body, html_body)
        
        if result:
            logger.info(f"Comment notification sent to {problem.author.email}")
        return result
        
    except Exception as e:
        logger.error(f"Comment notification error: {str(e)}")
        return False


def send_solution_notification(problem, solution):
    """Send notification for new solution"""
    if not problem.author.email_notifications:
        return False
        
    try:
        subject = f'New Solution Proposed - {problem.title}'
        text_body = f'''
Hi {problem.author.username},

{solution.proposer.username} proposed a solution to your problem "{problem.title}":

{solution.description}

View problem: http://127.0.0.1:5000/problem/{problem.id}

Best regards,
ProblemScope Team
'''
        
        try:
            html_body = render_template('email/solution_notification.html', 
                                       problem=problem, solution=solution)
        except:
            html_body = f"<html><body><pre>{text_body}</pre></body></html>"
        
        result = send_email(subject, [problem.author.email], text_body, html_body)
        
        if result:
            logger.info(f"Solution notification sent to {problem.author.email}")
        return result
        
    except Exception as e:
        logger.error(f"Solution notification error: {str(e)}")
        return False