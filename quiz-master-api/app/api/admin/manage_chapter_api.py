from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.chapter import Chapter
from app.models.subject import Subject
from app.schemas.chapter_schema import ChapterRequestSchema, ChapterEditRequestSchema
from sqlalchemy import or_
from flask_jwt_extended import jwt_required
from app.common.role_utils import roles_required
from app.common.enums import USER_ROLE
from app.common.utils import make_response
from app.extensions_redis import get_redis_client
import json

chapter_bp = Blueprint('chapter_bp', __name__)

@chapter_bp.route('/admin/chapter', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_chapters():
    redis_client = get_redis_client()
    cache_key = 'chapters:all'
    cached = redis_client.get(cache_key)
    if cached:
        return make_response(True, message="Chapters retrieved successfully (cache)", data=json.loads(cached)), 200
    chapters = Chapter.query.all()
    if not chapters:
        return make_response(False, error_message="No chapter found"), 404
    chapter_list = []
    for chapter in chapters:
        chapter_list.append({
            "id": chapter.id,
            "subject_id": chapter.subject_id,
            "subject_name": chapter.subject.name,
            "name": chapter.name,
            "description": chapter.description,
            "quizzes": chapter.quizzes.count()
        })
    redis_client.setex(cache_key, 300, json.dumps(chapter_list))
    return make_response(True, message="Chapters retrieved successfully", data=chapter_list), 200

@chapter_bp.route('/admin/chapter', methods=['POST'])
@jwt_required()
@roles_required(USER_ROLE[1])
def add_chapter():
    data = request.get_json()
    errors = ChapterRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    subject_id = data['subject_id']
    name = data['name']
    description = data['description']
    chapter = Chapter.query.filter_by(name=name).first()
    if chapter:
        current_app.logger.warning(f"Failed registration attempt for name: {name}, Chapter already exists")
        return make_response(False, error_message=f"Chapter {name} already exists"), 400
    new_chapter = Chapter(subject_id=subject_id, name=name, description=description)
    db.session.add(new_chapter)
    db.session.commit()
    current_app.logger.info(f"Chapter {new_chapter.name} registered successfully.")
    chapter_data = {
        "id": new_chapter.id,
        "subject_id": new_chapter.subject_id,
        "subject_name": new_chapter.subject.name,
        "name": new_chapter.name,
        "description": new_chapter.description,
        "quizzes": 0
    }
    redis_client = get_redis_client()
    redis_client.delete('chapters:all')
    return make_response(True, message="Subject registered successfully", data=chapter_data), 200

@chapter_bp.route('/admin/chapter/<int:id>', methods=['PUT'])
@jwt_required()
@roles_required(USER_ROLE[1])
def edit_chapter(id):       
    data = request.get_json()
    errors = ChapterRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    subject_id = data['subject_id']
    name = data['name']
    description = data['description']
    chapter = Chapter.query.get(id)
    if not chapter:
        current_app.logger.warning(f"Failed to edit chapter, chapter with ID {id} not found")
        return make_response(False, error_message=f"Chapter with ID {id} not found"), 400
    existing_chapter = Chapter.query.filter_by(name=name).first()
    if existing_chapter and existing_chapter.id != id:
        current_app.logger.warning(f"Failed registration attempt for name: {name}, Chapter already exists")
        return make_response(False, error_message=f"Chapter {name} already exists"), 400
    chapter.subject_id = subject_id
    chapter.name = name
    chapter.description = description
    db.session.commit()
    current_app.logger.info(f"Chapter {chapter.name} updated successfully.")
    chapter_data = {
        "id": chapter.id,
        "subject_id": chapter.subject_id,
        "subject_name": chapter.subject.name,
        "name": chapter.name,
        "description": chapter.description,
        "quizzes": chapter.quizzes.count()
    }
    redis_client = get_redis_client()
    redis_client.delete('chapters:all')
    return make_response(True, message="Chapter updated successfully", data=chapter_data), 200

@chapter_bp.route('/admin/chapter/<int:id>', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_chapter(id):
    chapter = Chapter.query.get(id)
    if not chapter:
        return make_response(False, error_message="Chapter not found"), 404
    chapter_data = {
        "id": chapter.id,
        "subject_id": chapter.subject_id,
        "subject_name": chapter.subject.name,
        "name": chapter.name,
        "description": chapter.description,
        "quizzes": chapter.quizzes.count()
    }
    return make_response(True, message="Subject retrieved successfully", data=chapter_data), 200

@chapter_bp.route('/admin/chapter/<int:id>', methods=['DELETE'])
@jwt_required()
@roles_required(USER_ROLE[1])
def delete_chapter(id):
    chapter = Chapter.query.get(id)
    if not chapter:
        return make_response(False, error_message="Chapter not found"), 404
    elif chapter.quizzes.count() > 0:
        return make_response(False, error_message="Cannot delete chapter with Quiz"), 400
    db.session.delete(chapter)
    db.session.commit()
    current_app.logger.info(f"Subject {chapter.name} deleted successfully.")
    redis_client = get_redis_client()
    redis_client.delete('chapters:all')
    return make_response(True, message=f"Subject {chapter.name} deleted successfully"), 200

@chapter_bp.route('/admin/chapter/<int:id>/quiz', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_chapter_quizzes(id):
    chapter = Chapter.query.get(id)
    if not chapter:
        return make_response(False, error_message="Chapter not found"), 404
    quiz_data = []
    for quiz in chapter.quizzes:
        quiz_data.append({
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "name": quiz.name,
            "description": quiz.description,
            "chapter_name": quiz.chapter.name if quiz.chapter_id else None,
            "subject_id": quiz.chapter.subject_id if quiz.chapter_id else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter_id else None,
            "start_date": quiz.start_date.strftime('%d-%m-%Y'),
            "end_date": quiz.end_date.strftime('%d-%m-%Y'),
            "duration": quiz.duration,
            "status": quiz.status,
            "questions": quiz.questions.count()
        })
    return make_response(True, message="Quiz retrieved successfully", data=quiz_data), 200

@chapter_bp.route('/admin/chapter/search', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def search_chapters():
    """ Search chapters by name, description, or subject name (query param: text) """
    text = request.args.get('text', '')
    current_app.logger.info(f"[DEBUG] Searching chapters with text: {text}")
    if not text or len(text) < 3:
        return make_response(False, error_message="Search text must be at least 3 characters long"), 400
    chapters = Chapter.query \
        .join(Chapter.subject) \
        .filter(
            or_(
                Chapter.name.ilike(f'%{text}%'),
                Chapter.description.ilike(f'%{text}%'),
                Subject.name.ilike(f'%{text}%')
            )
    ).all()
    if not chapters:
        return make_response(False, error_message="No chapters found"), 404
    chapter_list = []
    for chapter in chapters:
        chapter_list.append({
            "id": chapter.id,
            "subject_id": chapter.subject_id,
            "name": chapter.name,
            "description": chapter.description,
            "quizzes": chapter.quizzes.count()
        })
    current_app.logger.info(f"[DEBUG] Chapters search result: {chapter_list}")
    return make_response(True, message="Chapters retrieved successfully", data=chapter_list), 200