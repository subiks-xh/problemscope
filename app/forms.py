from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User
from flask_wtf.file import FileField, FileAllowed

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])
    location = StringField('Location', 
                          validators=[DataRequired(), Length(min=2, max=100)])
    skills = StringField('Skills (comma separated)', 
                        validators=[Length(max=200)])
    password = PasswordField('Password', 
                            validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one.')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    submit = SubmitField('Login')


# Problem Form
class ProblemForm(FlaskForm):
    title = StringField('Problem Title', 
                       validators=[DataRequired(), Length(min=10, max=200)])
    description = TextAreaField('Detailed Description', 
                               validators=[DataRequired(), Length(min=30)])
    category = SelectField('Category', 
                          choices=[
                              ('Environment', 'Environment'),
                              ('Education', 'Education'),
                              ('Health', 'Health'),
                              ('Infrastructure', 'Infrastructure'),
                              ('Technology', 'Technology'),
                              ('Social', 'Social Issues'),
                              ('Other', 'Other')
                          ],
                          validators=[DataRequired()])
    location = StringField('Location', 
                          validators=[DataRequired(), Length(min=3, max=100)])
    severity = SelectField('Severity Level', 
                          choices=[
                              ('Low', 'Low'),
                              ('Medium', 'Medium'),
                              ('High', 'High'),
                              ('Critical', 'Critical')
                          ],
                          validators=[DataRequired()])
    affected_count = IntegerField('Number of People Affected', 
                                 validators=[DataRequired(), NumberRange(min=1, max=1000000)])
    image = FileField('Upload Image (Optional)', 
                     validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Post Problem')

# Solution Form
class SolutionForm(FlaskForm):
    description = TextAreaField('Propose Your Solution', 
                               validators=[DataRequired(), Length(min=20)])
    submit = SubmitField('Submit Solution')


# Comment Form
class CommentForm(FlaskForm):
    content = TextAreaField('Your Comment', 
                           validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Post Comment')


# Verification Form
class VerificationForm(FlaskForm):
    proof_text = StringField('Proof/Evidence (optional)', 
                            validators=[Length(max=200)])
    submit = SubmitField('Verify This Problem')

# Request Password Reset Form (NEW)
class RequestResetForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


# Reset Password Form (NEW)
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', 
                            validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


# Update Profile Form (NEW)
class UpdateProfileForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])
    location = StringField('Location', 
                          validators=[Length(max=100)])
    skills = StringField('Skills (comma separated)', 
                        validators=[Length(max=200)])
    bio = TextAreaField('Bio', 
                       validators=[Length(max=500)])
    profile_picture = FileField('Update Profile Picture', 
                               validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    email_notifications = SelectField('Email Notifications', 
                                     choices=[('1', 'Enabled'), ('0', 'Disabled')])
    submit = SubmitField('Update Profile')


# Contact Form (NEW)
class ContactForm(FlaskForm):
    name = StringField('Your Name', 
                      validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Your Email', 
                       validators=[DataRequired(), Email()])
    subject = StringField('Subject', 
                         validators=[DataRequired(), Length(min=5, max=100)])
    message = TextAreaField('Message', 
                           validators=[DataRequired(), Length(min=20, max=1000)])
    submit = SubmitField('Send Message')


# Tag Form (NEW)
class TagForm(FlaskForm):
    tags = StringField('Tags (comma separated)', 
                      validators=[Length(max=200)])