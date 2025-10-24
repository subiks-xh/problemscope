from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    location = db.Column(db.String(100))
    skills = db.Column(db.String(200))  # Stored as comma-separated
    reputation_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(200), default='default.jpg')
    bio = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    problems = db.relationship('Problem', backref='author', lazy=True)
    solutions = db.relationship('Solution', backref='proposer', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def get_verification_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_email_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=3600)['user_id']
        except:
            return None
        return User.query.get(user_id)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# Problem Model
class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # Low, Medium, High, Critical
    affected_count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default='Pending Verification')
    # Status: Pending Verification, Verified, Solution Proposed, In Progress, Solved
    impact_score = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(200))
    verification_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    solutions = db.relationship('Solution', backref='problem', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='problem', lazy=True, cascade='all, delete-orphan')
    verifications = db.relationship('Verification', backref='problem', lazy=True, cascade='all, delete-orphan')
    
    def calculate_impact_score(self):
        """Calculate impact score based on severity, affected count, and time"""
        severity_weights = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        severity_value = severity_weights.get(self.severity, 1)
        
        # Days since creation
        days_old = (datetime.utcnow() - self.created_at).days + 1
        
        # Impact Score Formula
        self.impact_score = (self.affected_count * severity_value * 10) / days_old
        db.session.commit()
    
    def __repr__(self):
        return f"Problem('{self.title}', '{self.status}')"


# Solution Model
class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    votes = db.Column(db.Integer, default=0)
    feasibility_score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='Proposed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Solution('{self.id}', Problem: '{self.problem_id}')"


# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    
    def __repr__(self):
        return f"Comment('{self.id}', by User: '{self.user_id}')"


# Verification Model
class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proof_text = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    
    # Relationship
    verified_by = db.relationship('User', backref='verifications')
    
    def __repr__(self):
        return f"Verification(Problem: '{self.problem_id}', by User: '{self.user_id}')"
    
# Bookmark Model (NEW)
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    problem = db.relationship('Problem', backref='bookmarked_by')
    
    def __repr__(self):
        return f"Bookmark(User: '{self.user_id}', Problem: '{self.problem_id}')"


# Tag Model (NEW)
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"Tag('{self.name}')"


# ProblemTag Association (NEW)
class ProblemTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    
    # Relationships
    problem = db.relationship('Problem', backref='problem_tags')
    tag = db.relationship('Tag', backref='tagged_problems')


# Activity Feed (NEW)
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'posted_problem', 'added_solution', etc.
    description = db.Column(db.String(200), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='activities')
    problem = db.relationship('Problem', backref='activities')
    
    def __repr__(self):
        return f"Activity('{self.activity_type}', User: '{self.user_id}')"
# Vote Model (ADD THIS NEW MODEL)
class SolutionVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'), nullable=False)
    vote_type = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure user can only vote once per solution
    __table_args__ = (db.UniqueConstraint('user_id', 'solution_id', name='unique_user_solution_vote'),)
    
    def __repr__(self):
        return f"SolutionVote(User: '{self.user_id}', Solution: '{self.solution_id}', Type: '{self.vote_type}')"