from flask_mail import Message
from app import mail
from flask import current_app, render_template
from threading import Thread
import logging

logger = logging.getLogger(__name__)

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

def send_email(subject, recipients, text_body, html_body):
    """Send an email, returns True on success, False on failure"""
    try:
        msg = Message(subject, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)
        logger.info(f"Email sent to {recipients}: {subject}")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Email error: {str(e)}")
        return False


def send_verification_email(user, token):
    """Send email verification link to new user"""
    try:
        subject = 'Verify Your Email - ProblemScope'
        text_body = f'''Hi {user.username},

Please verify your email by clicking this link:
http://127.0.0.1:5000/verify_email/{token}

This link expires in 1 hour.

Best regards,
ProblemScope Team
'''
        try:
            html_body = render_template('email/verify_email.html', user=user, token=token)
        except Exception:
            html_body = f"<html><body><pre>{text_body}</pre></body></html>"
        
        return send_email(subject, [user.email], text_body, html_body)
    except Exception as e:
        logger.error(f"Verification email error: {str(e)}")
        return False


def send_password_reset_email(user, token):
    """Send password reset link email"""
    try:
        subject = 'Password Reset Request - ProblemScope'
        text_body = f'''Hi {user.username},

To reset your password, click this link:
http://127.0.0.1:5000/reset_password/{token}

If you didn't request this, ignore this email.
This link expires in 30 minutes.

Best regards,
ProblemScope Team
'''
        try:
            html_body = render_template('email/reset_password.html', user=user, token=token)
        except Exception:
            html_body = f'''
            <html><body style="font-family: Arial; padding: 20px;">
                <h2>Password Reset Request</h2>
                <p>Hi {user.username},</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="http://127.0.0.1:5000/reset_password/{token}"
                   style="background:#3498db;color:white;padding:10px 20px;
                          text-decoration:none;border-radius:5px;display:inline-block;"
                   >Reset Password</a></p>
                <p style="color:#e74c3c;">If you didn't request this, ignore this email.</p>
                <p style="color:#95a5a6;font-size:12px;">This link expires in 30 minutes.</p>
            </body></html>'''
        
        return send_email(subject, [user.email], text_body, html_body)
    except Exception as e:
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