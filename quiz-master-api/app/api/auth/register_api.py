from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.register_schema import RegisterRequestSchema
from app.common.utils import make_response

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = RegisterRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    fullname = data['fullname']
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()
    if user:
        return make_response(False, error_message="Email already exists, please use a different email"), 400
    new_user = User(fullname=fullname, email=email, password=password)
    db.session.add(new_user)
    db.session.flush()
    user_profile = UserProfile(user_id=new_user.id)
    db.session.add(user_profile)
    db.session.commit()
    return make_response(True, message="User registered successfully"), 200