from flask import render_template
from flask_login import login_required, current_user
from app.main import bp

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', name=current_user.username)
