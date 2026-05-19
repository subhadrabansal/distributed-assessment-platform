from flask import Blueprint, request, jsonify, current_app
from app.common.enums  import USER_ROLE, USER_STATUS
from app.extensions import db
from app.models.user import User
from app.models.score import Score
from app.schemas.user_profile_schema import UserProfileRequestSchema
from app.common.role_utils import roles_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from datetime import datetime
import os
import random
import string
from werkzeug.security import generate_password_hash
from app.common.utils import make_response
import json
from app.extensions_redis import get_redis_client

user_profile_bp = Blueprint('user_profile_bp', __name__)

@user_profile_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    user_id = None
    if isinstance(identity, str):
        import json
        identity = json.loads(identity)
        user_id = identity.get('id')
    user = User.query.get(user_id)
    if not user or not user.user_profile:
        return make_response(False, error_message="User profile not found"), 404
    profile = user.user_profile
    profile_data = {
        'fullname': user.fullname,
        'email': user.email,
        'profile_picture': profile.profile_picture,
        'phone_number': profile.phone_number,
        'date_of_birth': profile.date_of_birth.strftime('%d-%m-%Y') if profile.date_of_birth else None,
        'qualification': profile.qualification,
        'subject': profile.subject,
    }
    return make_response(True, message="Profile fetched successfully", data=profile_data), 200

@user_profile_bp.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    user_id = None
    if isinstance(identity, str):
        import json
        identity = json.loads(identity)
        user_id = identity.get('id')
    user = User.query.get(user_id)
    if not user or not user.user_profile:
        return make_response(False, error_message="User profile not found"), 404
    data = request.get_json()
    errors = UserProfileRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    profile = user.user_profile
    user.fullname = data.get('fullname', user.fullname)
    dob_str = data.get('date_of_birth')
    if dob_str:
        try:
            if '-' in dob_str:
                dob = datetime.strptime(dob_str, '%d-%m-%Y')
            else:
                dob = datetime.strptime(dob_str, '%d/%m/%Y')
            profile.date_of_birth = dob
        except Exception:
            return make_response(False, error_message="Invalid date format. Use DD-MM-YYYY or DD/MM/YYYY."), 400
    profile.phone_number = data.get('phone_number', profile.phone_number)
    profile.qualification = data.get('qualification', profile.qualification)
    profile.subject = data.get('subject', profile.subject)
    db.session.commit()
    profile_data = {
        'fullname': user.fullname,
        'email': user.email,
        'profile_picture': profile.profile_picture,
        'phone_number': profile.phone_number,
        'date_of_birth': profile.date_of_birth.strftime('%d-%m-%Y') if profile.date_of_birth else None,
        'qualification': profile.qualification,
        'subject': profile.subject,
    }
    return make_response(True, message="Profile updated successfully", data=profile_data), 200

@user_profile_bp.route('/auth/profile/upload_picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    if 'file' not in request.files:
        return make_response(False, error_message="No file part in the request"), 400
    file = request.files['file']
    if file.filename == '':
        return make_response(False, error_message="No selected file"), 400
    if file:
        key = ''.join(random.choices(string.digits, k=16))
        ext = os.path.splitext(file.filename)[1]
        base_name = os.path.splitext(secure_filename(file.filename))[0]
        filename = f'{key}_{base_name}{ext}'
        save_path = os.path.join(current_app.root_path, 'static', 'profile_pics', filename)
        while os.path.exists(save_path):
            key = ''.join(random.choices(string.digits, k=16))
            filename = f'{key}_{base_name}{ext}'
            save_path = os.path.join(current_app.root_path, 'static', 'profile_pics', filename)
        file.save(save_path)
        identity = get_jwt_identity()
        user_id = None
        if isinstance(identity, str):
            import json
            identity = json.loads(identity)
            user_id = identity.get('id')
        user = User.query.get(user_id)
        if not user or not user.user_profile:
            return make_response(False, error_message="User profile not found"), 404
        user.user_profile.profile_picture = filename
        db.session.commit()
        return make_response(True, message="Profile picture uploaded successfully", data={"profile_picture": f'/static/profile_pics/{filename}'}), 200

@user_profile_bp.route('/auth/profile/upload_password', methods=['PUT'])
@jwt_required()
def update_password():
    identity = get_jwt_identity()
    user_id = None
    if isinstance(identity, str):
        import json
        identity = json.loads(identity)
        user_id = identity.get('id')
    user = User.query.get(user_id)
    if not user:
        return make_response(False, error_message="User not found"), 404
    data = request.get_json()
    new_password = data.get('new_password')
    if not new_password:
        return make_response(False, error_message="New password is required"), 400
    user.password = generate_password_hash(new_password)
    db.session.commit()
    return make_response(True, message="Password updated successfully"), 200


@user_profile_bp.route('/auth/user', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])  
def get_users():
    redis_client = get_redis_client()
    cache_key = 'users:all'
    cached = redis_client.get(cache_key)
    if cached:
        return make_response(True, message="Users retrieved successfully (cache)", data=json.loads(cached)), 200
    users = User.query.filter(User.role != USER_ROLE[1]).all()  
    user_list=[]
    for user in users:
        if user.user_profile:
            user_data = {
                'id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'status': user.status == 'active',  # Always boolean
                'profile_picture': user.user_profile.profile_picture,
                'phone_number': user.user_profile.phone_number,
                'date_of_birth': user.user_profile.date_of_birth.strftime('%d-%m-%Y') if user.user_profile.date_of_birth else None,
                'qualification': user.user_profile.qualification,
                'subject': user.user_profile.subject,
                'quiz_count': len(Score.query.filter_by(user_id=user.id).all())
            }
            user_list.append(user_data)
    redis_client.setex(cache_key, 300, json.dumps(user_list))
    return make_response(True, message="Users retrieved successfully", data=user_list), 200

@user_profile_bp.route('/auth/user/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@roles_required(USER_ROLE[1])
def update_user_status(user_id):
    user = User.query.get(user_id)
    if not user:
        return make_response(False, error_message="User not found"), 404
    user.status = USER_STATUS[1] if user.status == USER_STATUS[0] else USER_STATUS[0]
    db.session.commit()
    redis_client = get_redis_client()
    redis_client.delete('users:all')
    user_data = {
        'id': user.id,
        'fullname': user.fullname,
        'email': user.email,
        'status': user.status == USER_STATUS[1],  
        'profile_picture': user.user_profile.profile_picture if user.user_profile else None,
        'phone_number': user.user_profile.phone_number if user.user_profile else None,
        'date_of_birth': user.user_profile.date_of_birth.strftime('%d-%m-%Y') if user.user_profile and user.user_profile.date_of_birth else None,
        'qualification': user.user_profile.qualification if user.user_profile else None,
        'subject': user.user_profile.subject if user.user_profile else None,
        'quiz_count': len(Score.query.filter_by(user_id=user.id).all())
    }
    return make_response(True, message=f"User status updated to {user.status}", data=user_data), 200


@user_profile_bp.route('/auth/user/<string:text>/search', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def search_users(text):
    users = User.query.filter(
    and_(
        or_(
            User.fullname.ilike(f'%{text}%'),
            User.email.ilike(f'%{text}%')
        ),
        User.role != USER_ROLE[1]
    )
).all()
    user_list = []
    for user in users:
        if user.user_profile:
            user_data = {
                'id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'status': user.status == 'active',
                'profile_picture': user.user_profile.profile_picture,
                'phone_number': user.user_profile.phone_number,
                'date_of_birth': user.user_profile.date_of_birth.strftime('%d-%m-%Y') if user.user_profile.date_of_birth else None,
                'qualification': user.user_profile.qualification,
                'subject': user.user_profile.subject,
                'quiz_count': len(Score.query.filter_by(user_id=user.id).all())
            }
            user_list.append(user_data)
    return make_response(True, message="User list fetched successfully", data=user_list), 200
