from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.subject import Subject
from app.schemas.subject_schema import SubjectRequestSchema, SubjectEditRequestSchema
from app.common.validation import validate_request
from app.common.role_utils import roles_required
from app.common.enums import USER_ROLE
from app.common.utils import make_response
from app.extensions_redis import get_redis_client
import json

subject_bp = Blueprint('subject_bp', __name__)

@subject_bp.route('/admin/subject', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_subjects():
    redis_client = get_redis_client()
    cache_key = 'subjects:all'
    cached = redis_client.get(cache_key)
    if cached:
        current_app.logger.info("[DEBUG] Returning subjects from Redis cache")
        return make_response(True, message="Subjects retrieved successfully (cache)", data=json.loads(cached)), 200

    current_app.logger.info("[DEBUG] Fetching all subjects from DB")
    subjects = Subject.query.all()
    if not subjects:
        return make_response(False, error_message="No subjects found"), 404
    subject_list = []
    for subject in subjects:
        subject_list.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "chapters": subject.chapters.count()
        })
    current_app.logger.info(f"[DEBUG] Subjects fetched: {subject_list}")
    redis_client.setex(cache_key, 300, json.dumps(subject_list))  # Cache for 5 minutes
    return make_response(True, message="Subjects retrieved successfully", data=subject_list), 200

@subject_bp.route('/admin/subject', methods=['POST'])
@jwt_required()
@roles_required(USER_ROLE[1])
def add_subject():
    data = request.get_json()
    current_app.logger.info(f"[DEBUG] Incoming subject add data: {data}")
    errors = SubjectRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    name = data['name']
    description = data['description']
    subject = Subject.query.filter_by(name=name).first()
    if subject:
        current_app.logger.warning(f"Failed registration attempt for name: {name}, Subject already exists")
        return make_response(False, error_message=f"Subject {name} already exists"), 400
    new_subject = Subject(name=name, description=description)
    db.session.add(new_subject)
    db.session.commit()
    current_app.logger.info(f"Subject {new_subject.name} registered successfully.")
    subject_data = {
        "id": new_subject.id,
        "name": new_subject.name,
        "description": new_subject.description,
        "chapters": 0
    }
    # Invalidate cache after mutation
    redis_client = get_redis_client()
    redis_client.delete('subjects:all')
    return make_response(True, message="Subject registered successfully", data=subject_data), 200

@subject_bp.route('/admin/subject/<int:id>', methods=['PUT'])
@jwt_required()
@roles_required(USER_ROLE[1])
def edit_subject(id):
    data = request.get_json()
    current_app.logger.info(f"[DEBUG] Incoming subject update data: {data}")
    errors = SubjectRequestSchema().validate(data)
    name = data['name']
    description = data['description']
    if errors:
        return make_response(False, error_message=errors), 400
    subject = Subject.query.get(id)
    if not subject:
        current_app.logger.warning(f"Failed to edit subject, Subject with ID {id} not found")
        return make_response(False, error_message=f"Subject with ID {id} not found"), 400
    existing_subject = Subject.query.filter_by(name=name).first()
    if existing_subject and existing_subject.id != id:
        current_app.logger.warning(f"Failed registration attempt for name: {name}, Subject already exists")
        return make_response(False, error_message=f"Subject {name} already exists"), 400
    subject.name = name
    subject.description = description
    db.session.commit()
    current_app.logger.info(f"Subject {subject.name} updated successfully.")
    subject_data = {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "chapters": subject.chapters.count()
    }
    redis_client = get_redis_client()
    redis_client.delete('subjects:all')
    return make_response(True, message="Subject updated successfully", data=subject_data), 200

@subject_bp.route('/admin/subject/<int:id>', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_subject(id):
    current_app.logger.info(f"[DEBUG] Fetching subject with id: {id}")
    subject = Subject.query.get(id)
    if not subject:
        return make_response(False, error_message="Subject not found"), 404
    subject_data = {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "chapters": subject.chapters.count()
    }
    current_app.logger.info(f"[DEBUG] Subject fetched: {subject_data}")
    return make_response(True, message="Subject retrieved successfully", data=subject_data), 200

@subject_bp.route('/admin/subject/<int:id>', methods=['DELETE'])
@jwt_required()
@roles_required(USER_ROLE[1])
def delete_subject(id):
    current_app.logger.info(f"[DEBUG] Deleting subject with id: {id}")
    subject = Subject.query.get(id)
    if not subject:
        return make_response(False, error_message="Subject not found"), 404
    elif subject.chapters.count() > 0:
        return make_response(False, error_message="Cannot delete subject with chapters"), 400
    db.session.delete(subject)
    db.session.commit()
    current_app.logger.info(f"Subject {subject.name} deleted successfully.")
    # Invalidate cache after mutation
    redis_client = get_redis_client()
    redis_client.delete('subjects:all')
    return make_response(True, message=f"Subject {subject.name} deleted successfully"), 200

@subject_bp.route('/admin/subject/<int:id>/chapters', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_subject_chapters(id):
    current_app.logger.info(f"[DEBUG] Fetching chapters for subject id: {id}")
    subject = Subject.query.get(id)
    if not subject:
        return make_response(False, error_message="Subject not found"), 404
    chapters = subject.chapters.all()
    chapter_list = []
    for chapter in chapters:
        chapter_list.append({
            "id": chapter.id,
            "subject_id": chapter.subject_id,
            "name": chapter.name,
            "description": chapter.description,
            "quizzes": chapter.quizzes.count()
        })
    current_app.logger.info(f"[DEBUG] Chapters fetched for subject {id}: {chapter_list}")
    return make_response(True, message="Chapters retrieved successfully", data=chapter_list), 200

@subject_bp.route('/admin/subject/search', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def search_subjects():
    """ Search subjects by name or description (query param: text) """
    text = request.args.get('text', '')
    current_app.logger.info(f"[DEBUG] Searching subjects with text: {text}")
    if not text or len(text.strip()) < 3:
        return make_response(False, error_message="Search text cannot be empty or less than 3 characters"), 400
    subjects = Subject.query.filter(
        Subject.name.ilike(f'%{text}%') | Subject.description.ilike(f'%{text}%')
    ).all()
    if not subjects:
        return make_response(False, error_message="No subjects found"), 404
    subject_list = []
    for subject in subjects:
        subject_list.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "chapters": subject.chapters.count()
        })
    current_app.logger.info(f"[DEBUG] Subjects search result: {subject_list}")
    return make_response(True, message="Subjects retrieved successfully", data=subject_list), 200