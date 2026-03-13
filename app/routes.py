from flask import render_template, url_for, flash, redirect, request, current_app as app, abort, send_file
from urllib.parse import urlparse
from app import db, bcrypt, limiter
from app.models import User, Problem, Solution, Comment, Verification, SolutionVote, Bookmark, Tag, ProblemTag, Activity
from app.forms import (RegistrationForm, LoginForm, ProblemForm, SolutionForm, CommentForm, 
                       VerificationForm, RequestResetForm, ResetPasswordForm, UpdateProfileForm, ContactForm)
from flask_login import login_user, current_user, logout_user, login_required
from app.utils import save_picture, log_activity
from app.email import send_verification_email, send_password_reset_email, send_comment_notification, send_solution_notification, send_email
from sqlalchemy import or_, and_, func
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ==========================================
# HOME & SEARCH
# ==========================================

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    severity_filter = request.args.get('severity', '')
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'impact')
    
    query = Problem.query
    
    if search_query:
        query = query.filter(
            or_(
                Problem.title.ilike(f'%{search_query}%'),
                Problem.description.ilike(f'%{search_query}%'),
                Problem.location.ilike(f'%{search_query}%')
            )
        )
    
    if category_filter:
        query = query.filter(Problem.category == category_filter)
    
    if severity_filter:
        query = query.filter(Problem.severity == severity_filter)
    
    if status_filter:
        query = query.filter(Problem.status == status_filter)
    
    if sort_by == 'impact':
        query = query.order_by(Problem.impact_score.desc())
    elif sort_by == 'date':
        query = query.order_by(Problem.created_at.desc())
    elif sort_by == 'affected':
        query = query.order_by(Problem.affected_count.desc())
    elif sort_by == 'verifications':
        query = query.order_by(Problem.verification_count.desc())
    
    problems_paginated = query.paginate(page=page, per_page=6, error_out=False)
    
    for problem in problems_paginated.items:
        problem.calculate_impact_score()
    
    all_problems = Problem.query.all()
    total_problems = len(all_problems)
    solved_problems = sum(1 for p in all_problems if p.status == 'Solved')
    verified_problems = sum(1 for p in all_problems if p.status == 'Verified')
    
    return render_template('home.html', 
                          problems=problems_paginated,
                          total_problems=total_problems,
                          solved_problems=solved_problems,
                          verified_problems=verified_problems,
                          search_query=search_query,
                          category_filter=category_filter,
                          severity_filter=severity_filter,
                          status_filter=status_filter,
                          sort_by=sort_by)


# ==========================================
# AUTHENTICATION
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            location=form.location.data,
            skills=form.skills.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        token = user.get_verification_token()
        send_verification_email(user, token)
        
        log_activity(user.id, 'joined', f'{user.username} joined ProblemScope')
        
        flash(f'Account created! Please check your email to verify your account.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)


@app.route('/verify_email/<token>')
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('home'))
    
    user.is_verified = True
    db.session.commit()
    
    flash('Your email has been verified! You can now log in.', 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_verified:
                flash('Please verify your email address before logging in. Check your inbox for the verification link.', 'warning')
                return render_template('login.html', title='Login', form=form)
            login_user(user)
            user.last_seen = datetime.utcnow()
            db.session.commit()
            
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            # Prevent open redirect: only allow local paths
            if next_page and urlparse(next_page).netloc:
                next_page = None
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login failed. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ==========================================
# PASSWORD RESET
# ==========================================

@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            try:
                token = user.get_reset_token()
                result = send_password_reset_email(user, token)
                if result:
                    flash('Password reset instructions have been sent to your email. Check spam folder too!', 'success')
                else:
                    flash('Failed to send reset email. Please try again later.', 'danger')
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash('An error occurred while sending the reset email. Please try again.', 'danger')
        else:
            # Vague message to prevent user enumeration
            flash('If that email is registered, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', title='Reset Password', form=form)


# ==========================================
# PROBLEMS
# ==========================================

@app.route('/problem/new', methods=['GET', 'POST'])
@login_required
def new_problem():
    form = ProblemForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = save_picture(form.image.data, 'problems')
        
        problem = Problem(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            location=form.location.data,
            severity=form.severity.data,
            affected_count=form.affected_count.data,
            image_url=image_file,
            author=current_user
        )
        
        db.session.add(problem)
        db.session.commit()
        
        problem.calculate_impact_score()
        
        log_activity(current_user.id, 'posted_problem', 
                    f'{current_user.username} posted: {problem.title}', 
                    problem.id)
        
        flash('Your problem has been posted!', 'success')
        return redirect(url_for('home'))
    
    return render_template('create_problem.html', title='New Problem', form=form, legend='Post a Problem')


@app.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem_detail(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    solution_form = SolutionForm()
    comment_form = CommentForm()
    verification_form = VerificationForm()
    
    if solution_form.validate_on_submit() and current_user.is_authenticated:
        solution = Solution(
            description=solution_form.description.data,
            problem_id=problem.id,
            user_id=current_user.id
        )
        db.session.add(solution)
        
        if problem.status == 'Verified':
            problem.status = 'Solution Proposed'
        
        db.session.commit()
        
        log_activity(current_user.id, 'added_solution', 
                    f'{current_user.username} proposed a solution', 
                    problem.id)
        
        send_solution_notification(problem, solution)
        
        flash('Solution submitted successfully!', 'success')
        return redirect(url_for('problem_detail', problem_id=problem.id))
    
    if comment_form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=comment_form.content.data,
            problem_id=problem.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        
        log_activity(current_user.id, 'added_comment', 
                    f'{current_user.username} commented on a problem', 
                    problem.id)
        
        send_comment_notification(problem, comment)
        
        flash('Comment added!', 'success')
        return redirect(url_for('problem_detail', problem_id=problem.id))
    
    solutions = Solution.query.filter_by(problem_id=problem.id).order_by(Solution.votes.desc()).all()
    comments = Comment.query.filter_by(problem_id=problem.id).order_by(Comment.created_at.desc()).all()
    
    is_bookmarked = False
    if current_user.is_authenticated:
        is_bookmarked = Bookmark.query.filter_by(user_id=current_user.id, problem_id=problem.id).first() is not None
    
    return render_template('problem_detail.html', 
                          title=problem.title, 
                          problem=problem, 
                          solutions=solutions,
                          comments=comments,
                          solution_form=solution_form,
                          comment_form=comment_form,
                          verification_form=verification_form,
                          is_bookmarked=is_bookmarked)


@app.route('/problem/<int:problem_id>/verify', methods=['POST'])
@login_required
def verify_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    
    existing = Verification.query.filter_by(user_id=current_user.id, problem_id=problem.id).first()
    
    if existing:
        flash('You have already verified this problem.', 'warning')
    else:
        verification = Verification(
            user_id=current_user.id,
            problem_id=problem.id,
            proof_text=request.form.get('proof_text', '')
        )
        
        db.session.add(verification)
        problem.verification_count += 1
        
        if problem.verification_count >= 3 and problem.status == 'Pending Verification':
            problem.status = 'Verified'
            flash('Problem has been verified!', 'success')
        
        db.session.commit()
        
        log_activity(current_user.id, 'verified_problem', 
                    f'{current_user.username} verified a problem', 
                    problem.id)
        
        flash('Thank you for verifying this problem!', 'success')
    
    return redirect(url_for('problem_detail', problem_id=problem.id))


@app.route('/problem/<int:problem_id>/update_status/<string:new_status>', methods=['POST'])
@login_required
def update_problem_status(problem_id, new_status):
    problem = Problem.query.get_or_404(problem_id)
    
    if problem.author != current_user:
        flash('You can only update your own problems!', 'danger')
        return redirect(url_for('problem_detail', problem_id=problem_id))
    
    valid_statuses = ['Pending Verification', 'Verified', 'Solution Proposed', 'In Progress', 'Solved']
    
    if new_status in valid_statuses:
        problem.status = new_status
        
        if new_status == 'Solved':
            current_user.reputation_points += 10
            log_activity(current_user.id, 'solved_problem', 
                        f'{current_user.username} solved: {problem.title}', 
                        problem.id)
            flash('🎉 Congratulations! Problem marked as Solved! You earned 10 reputation points!', 'success')
        else:
            flash(f'Problem status updated to: {new_status}', 'success')
        
        db.session.commit()
    else:
        flash('Invalid status!', 'danger')
    
    return redirect(url_for('problem_detail', problem_id=problem_id))


# ==========================================
# VOTING
# ==========================================

@app.route('/solution/<int:solution_id>/vote/<int:vote_type>', methods=['POST'])
@login_required
def vote_solution(solution_id, vote_type):
    solution = Solution.query.get_or_404(solution_id)
    
    existing_vote = SolutionVote.query.filter_by(
        user_id=current_user.id, 
        solution_id=solution_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type != vote_type:
            solution.votes += (vote_type * 2)
            existing_vote.vote_type = vote_type
        else:
            solution.votes -= vote_type
            db.session.delete(existing_vote)
    else:
        new_vote = SolutionVote(
            user_id=current_user.id,
            solution_id=solution_id,
            vote_type=vote_type
        )
        solution.votes += vote_type
        db.session.add(new_vote)
    
    solution.feasibility_score = solution.votes
    
    if vote_type == 1:
        solution.proposer.reputation_points += 2
    
    db.session.commit()
    flash('Vote recorded!', 'success')
    return redirect(url_for('problem_detail', problem_id=solution.problem_id))


# ==========================================
# BOOKMARKS
# ==========================================

@app.route('/problem/<int:problem_id>/bookmark', methods=['POST'])
@login_required
def bookmark_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    
    existing = Bookmark.query.filter_by(user_id=current_user.id, problem_id=problem_id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash('Bookmark removed.', 'info')
    else:
        bookmark = Bookmark(user_id=current_user.id, problem_id=problem_id)
        db.session.add(bookmark)
        db.session.commit()
        flash('Problem bookmarked!', 'success')
    
    return redirect(url_for('problem_detail', problem_id=problem_id))


@app.route('/bookmarks')
@login_required
def bookmarks():
    user_bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    # Filter out any bookmarks whose problem was deleted
    bookmarked_problems = [b.problem for b in user_bookmarks if b.problem is not None]
    
    return render_template('bookmarks.html', problems=bookmarked_problems, title='My Bookmarks')


# ==========================================
# USER PROFILE
# ==========================================

@app.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    problems = Problem.query.filter_by(user_id=user.id).order_by(Problem.created_at.desc()).all()
    solutions = Solution.query.filter_by(user_id=user.id).order_by(Solution.created_at.desc()).all()
    
    solved_problems = Problem.query.filter_by(user_id=user.id, status='Solved').count()
    total_impact = sum([p.impact_score for p in problems])
    
    return render_template('user_profile.html', 
                          user=user, 
                          problems=problems,
                          solutions=solutions,
                          solved_problems=solved_problems,
                          total_impact=total_impact)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    
    if form.validate_on_submit():
        # Check username uniqueness if it changed
        if form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('That username is already taken. Please choose another.', 'danger')
                return render_template('edit_profile.html', title='Edit Profile', form=form)
        
        # Check email uniqueness if it changed
        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('That email address is already registered.', 'danger')
                return render_template('edit_profile.html', title='Edit Profile', form=form)
        
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data, 'profiles')
            current_user.profile_picture = picture_file
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.location = form.location.data
        current_user.skills = form.skills.data
        current_user.bio = form.bio.data
        current_user.email_notifications = bool(int(form.email_notifications.data))
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user_profile', username=current_user.username))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.location.data = current_user.location
        form.skills.data = current_user.skills
        form.bio.data = current_user.bio
        form.email_notifications.data = str(int(current_user.email_notifications))
    
    return render_template('edit_profile.html', title='Edit Profile', form=form)


# ==========================================
# DASHBOARD
# ==========================================

@app.route('/dashboard')
@login_required
def dashboard():
    user_problems = Problem.query.filter_by(user_id=current_user.id).all()
    user_solutions = Solution.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard.html', 
                          title='Dashboard', 
                          problems=user_problems,
                          solutions=user_solutions)


# ==========================================
# ANALYTICS
# ==========================================

@app.route('/analytics')
def analytics():
    total_problems = Problem.query.count()
    total_users = User.query.count()
    total_solutions = Solution.query.count()
    solved_problems = Problem.query.filter_by(status='Solved').count()
    
    categories = db.session.query(
        Problem.category, 
        func.count(Problem.id)
    ).group_by(Problem.category).all()
    
    severities = db.session.query(
        Problem.severity, 
        func.count(Problem.id)
    ).group_by(Problem.severity).all()
    
    statuses = db.session.query(
        Problem.status, 
        func.count(Problem.id)
    ).group_by(Problem.status).all()
    
    top_contributors = db.session.query(
        User.username,
        User.reputation_points,
        func.count(Problem.id).label('problem_count')
    ).join(Problem).group_by(User.id).order_by(User.reputation_points.desc()).limit(5).all()
    
    recent_problems = Problem.query.order_by(Problem.created_at.desc()).limit(5).all()
    
    return render_template('analytics.html',
                          total_problems=total_problems,
                          total_users=total_users,
                          total_solutions=total_solutions,
                          solved_problems=solved_problems,
                          categories=categories,
                          severities=severities,
                          statuses=statuses,
                          top_contributors=top_contributors,
                          recent_problems=recent_problems)


# ==========================================
# ACTIVITY FEED
# ==========================================

@app.route('/activity')
def activity_feed():
    page = request.args.get('page', 1, type=int)
    activities = Activity.query.order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('activity_feed.html', activities=activities, title='Activity Feed')


# ==========================================
# ADMIN PANEL
# ==========================================

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403)
    
    total_users = User.query.count()
    total_problems = Problem.query.count()
    pending_verifications = Problem.query.filter_by(status='Pending Verification').count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_problems = Problem.query.order_by(Problem.created_at.desc()).limit(10).all()
    
    return render_template('admin_panel.html',
                          total_users=total_users,
                          total_problems=total_problems,
                          pending_verifications=pending_verifications,
                          recent_users=recent_users,
                          recent_problems=recent_problems)


@app.route('/admin/delete_problem/<int:problem_id>', methods=['POST'])
@login_required
def admin_delete_problem(problem_id):
    if not current_user.is_admin:
        abort(403)
    
    problem = Problem.query.get_or_404(problem_id)
    # Delete records not covered by the cascade (Bookmarks, ProblemTags, Activities)
    Bookmark.query.filter_by(problem_id=problem_id).delete()
    ProblemTag.query.filter_by(problem_id=problem_id).delete()
    Activity.query.filter_by(problem_id=problem_id).delete()
    db.session.delete(problem)
    db.session.commit()
    
    flash('Problem deleted by admin.', 'warning')
    return redirect(url_for('admin_panel'))


@app.route('/admin/make_admin/<int:user_id>', methods=['POST'])
@login_required
def make_admin(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = "Admin" if user.is_admin else "Regular User"
    flash(f'{user.username} is now a {status}.', 'success')
    return redirect(url_for('admin_panel'))


# ==========================================
# EXPORT TO PDF
# ==========================================

@app.route('/problem/<int:problem_id>/export_pdf')
@login_required
def export_problem_pdf(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "ProblemScope - Problem Report")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 100, "Title:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 120, problem.title[:80])
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 160, "Description:")
    p.setFont("Helvetica", 10)
    
    text = problem.description
    lines = [text[i:i+80] for i in range(0, len(text), 80)]
    y = height - 180
    for line in lines[:10]:
        p.drawString(50, y, line)
        y -= 15
    
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Category: {problem.category}")
    p.drawString(250, y, f"Severity: {problem.severity}")
    y -= 20
    p.drawString(50, y, f"Location: {problem.location}")
    p.drawString(250, y, f"Status: {problem.status}")
    y -= 20
    p.drawString(50, y, f"Affected People: {problem.affected_count}")
    p.drawString(250, y, f"Impact Score: {problem.impact_score:.1f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'problem_{problem_id}.pdf', mimetype='application/pdf')


# ==========================================
# CONTACT & ABOUT
# ==========================================

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_email(
            subject=f'Contact Form: {form.subject.data}',
            recipients=[current_app.config['ADMIN_EMAIL']],
            text_body=f'From: {form.name.data} ({form.email.data})\n\n{form.message.data}',
            html_body=f'<p><strong>From:</strong> {form.name.data} ({form.email.data})</p><p>{form.message.data}</p>'
        )
        
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('home'))
    
    return render_template('contact.html', title='Contact Us', form=form)


@app.route('/about')
def about():
    return render_template('about.html', title='About')