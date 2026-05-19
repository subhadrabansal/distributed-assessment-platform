from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db
from werkzeug.security import check_password_hash
from app.schemas.login_schema import LoginRequestSchema
from werkzeug.security import generate_password_hash
from app.common.enums import USER_ROLE
from app.common.utils import make_response, send_email
from app.models.otp import Otp
from datetime import datetime, timedelta
import random, string
import json

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    errors = LoginRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        user.last_login = datetime.now()
        db.session.commit()
        
        identity = json.dumps({'id': user.id, 'roles': user.role})
        token = create_access_token(identity=identity)
        user_data = {
            'id': user.id,
            "username": user.fullname,
            "roles": user.role,
            "isAdmin": user.has_role(USER_ROLE[1]),
            "token": token,
            "email": user.email,
            "profile_picture": url_for('static', filename=f'profile_pics/{user.user_profile.profile_picture}', _external=True),
        }
        update_all_quiz_statuses()
        return make_response(True, message="Login successful", data=user_data), 200
    else:
        return make_response(False, error_message="Invalid email or password"), 401


@login_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(False, error_message="Email does not exist!"), 404
    otp_code = ''.join(random.choices(string.digits, k=6))
    subject = "Distributed Assessment Platform Password Reset OTP"
    body = f"Your OTP for password reset is: {otp_code}"
    if not send_email(email, subject, body):
        return make_response(False, error_message="Failed to send OTP email."), 500
    otp = Otp(user_id=user.id, opt_code=otp_code, send_date=datetime.now(), active=1)
    db.session.add(otp)
    db.session.commit()
    return make_response(True, message="OTP sent to your email."), 200

@login_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp_code = data.get('otp')
    new_password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(False, error_message="Email does not exist!"), 404
    now = datetime.now()
    thirty_minutes_ago = now - timedelta(minutes=30)
    otp = Otp.query.filter_by(user_id=user.id, opt_code=otp_code, active=1).order_by(Otp.id.desc()).first()
    if not otp or otp.send_date < thirty_minutes_ago:
        return make_response(False, error_message="Invalid or expired OTP!"), 400
    
    user.password = generate_password_hash(new_password)
    otp.active = 0
    db.session.commit()
    return make_response(True, message="Password reset successful."), 200


def update_all_quiz_statuses():
    """Update all quiz statuses based on current date/time during login"""
    from app.common.quiz_status_manager import QuizStatusManager
    try:
        result = QuizStatusManager.update_all_quiz_statuses(context='login')
        if result['updated_count'] > 0:
            current_app.logger.info(f"Login triggered quiz status updates: {result['updated_count']} quizzes updated")
    except Exception as e:
        current_app.logger.error(f"Error updating quiz statuses during login: {e}")
