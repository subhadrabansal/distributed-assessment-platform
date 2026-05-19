from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject
from app.schemas.quiz_schema import QuizRequestSchema, QuizEditRequestSchema
from app.common.enums import QUIZ_STATUSES
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from flask_jwt_extended import jwt_required
from app.common.role_utils import roles_required
from app.common.enums import USER_ROLE
from app.common.utils import make_response
from app.extensions_redis import get_redis_client
import json

quiz_bp = Blueprint('quiz_bp', __name__)

def clear_quiz_cache():
    """Helper function to clear quiz-related Redis cache"""
    try:
        redis_client = get_redis_client()
        cache_key = 'quizzes:all'
        result = redis_client.delete(cache_key)
        current_app.logger.info(f"Quiz cache cleared (keys deleted: {result})")
        return result
    except Exception as e:
        current_app.logger.error(f"Failed to clear quiz cache: {str(e)}")
        return 0

@quiz_bp.route('/admin/quiz', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_quizzes():
    redis_client = get_redis_client()
    cache_key = 'quizzes:all'
    
    try:
        cached = redis_client.get(cache_key)
        if cached:
            current_app.logger.info("Retrieved quizzes from Redis cache")
            return make_response(True, message="Quizzes retrieved successfully (cache)", data=json.loads(cached)), 200
    except Exception as e:
        current_app.logger.warning(f"Redis cache read failed: {str(e)}, fetching from database")
    
    quizzes = Quiz.query.all()
    if not quizzes:
        return make_response(False, error_message="No quiz found"), 404
        
    quiz_list = []
    for quiz in quizzes:
        quiz_list.append({
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
    
    try:
        redis_client.setex(cache_key, 60, json.dumps(quiz_list))
        current_app.logger.info(f"Cached {len(quiz_list)} quizzes in Redis")
    except Exception as e:
        current_app.logger.warning(f"Failed to cache quizzes in Redis: {str(e)}")
    
    return make_response(True, message="Quizzes retrieved successfully", data=quiz_list), 200

@quiz_bp.route('/admin/quiz', methods=['POST'])
@jwt_required()
@roles_required(USER_ROLE[1])
def add_quiz():
    data = request.get_json()
    chapter_id = data.get('chapter_id')
    name = data.get('name')
    description = data.get('description')
    start_date = datetime.strptime(data.get('start_date'), '%d-%m-%Y')
    end_date = datetime.strptime(data.get('end_date'), '%d-%m-%Y')
    duration = data.get('duration')

    quiz = Quiz.query.filter_by(name=name).first()
    if quiz:
        current_app.logger.warning(f"Failed registration attempt for name: {name}, quiz already exists")
        return make_response(False, error_message=f"Quiz {name} already exists"), 400

    new_quiz = Quiz(
        chapter_id=chapter_id,
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        duration=duration
    )

    db.session.add(new_quiz)
    db.session.commit()

    clear_quiz_cache()

    current_app.logger.info(f"Quiz {new_quiz.name} registered successfully.")
    
    response_data = {
        "id": new_quiz.id,
        "chapter_id": new_quiz.chapter_id,
        "name": new_quiz.name,
        "description": new_quiz.description,
        "chapter_name": new_quiz.chapter.name if new_quiz.chapter_id else None,
        "subject_id": new_quiz.chapter.subject_id if new_quiz.chapter_id else None,
        "subject_name": new_quiz.chapter.subject.name if new_quiz.chapter_id else None,
        "start_date": new_quiz.start_date.strftime('%d-%m-%Y'),
        "end_date": new_quiz.end_date.strftime('%d-%m-%Y'),
        "duration": new_quiz.duration,
        "questions": 0
    }

    return make_response(True, message="Quiz registered successfully", data=response_data), 201

@quiz_bp.route('/admin/quiz/<int:id>', methods=['PUT'])
@jwt_required()
@roles_required(USER_ROLE[1])
def edit_quiz(id):
    data = request.get_json()
    chapter_id = data.get('chapter_id')
    name = data.get('name')
    description = data.get('description')
    start_date = datetime.strptime(data.get('start_date'), '%d-%m-%Y')
    end_date = datetime.strptime(data.get('end_date'), '%d-%m-%Y')
    duration = data.get('duration')

    quiz = Quiz.query.get(id)
    if not quiz:
        current_app.logger.warning(f"Failed to edit chapter, quiz with ID {id} not found")
        return make_response(False, error_message=f"Quiz with ID {id} not found"), 404
    
    existing_quiz = Quiz.query.filter_by(name=name).first()
    if existing_quiz and existing_quiz.id != id:
        current_app.logger.warning(f"Failed registration attempt for name: {name}, quiz already exists")
        return make_response(False, error_message=f"Quiz {name} already exists"), 400
    
    quiz.chapter_id = chapter_id
    quiz.name = name
    quiz.description = description
    quiz.start_date = start_date
    quiz.end_date = end_date
    quiz.duration = duration

    db.session.commit()
    current_app.logger.info(f"Quiz {quiz.name} updated successfully.")
    
    clear_quiz_cache()
    
    response_data = {
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
        "questions": quiz.questions.count()
    }
    return make_response(True, message="Quiz updated successfully", data=response_data), 200

@quiz_bp.route('/admin/quiz/<int:id>', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_quiz(id):
    quiz = Quiz.query.get(id)
    if not quiz:
        return make_response(False, error_message="Quiz not found"), 404

    quiz_data = {
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
    }

    return make_response(True, message="Quiz retrieved successfully", data=quiz_data), 200

@quiz_bp.route('/admin/quiz/<int:id>', methods=['DELETE'])
@jwt_required()
@roles_required(USER_ROLE[1])
def delete_quiz(id):
    quiz = Quiz.query.get(id)
    if not quiz:
        return make_response(False, error_message="Quiz not found"), 404
    if quiz.status != QUIZ_STATUSES[0]:
        return make_response(False, error_message=f"Quiz cannot be deleted because it is not in the {QUIZ_STATUSES[0]} state."), 400
    else:
        for question in quiz.questions:
            db.session.delete(question)
        db.session.delete(quiz)
        db.session.commit()
        current_app.logger.info(f"Quiz {quiz.name} deleted successfully with Questions.")
        
        clear_quiz_cache()
        
        return make_response(True, message=f"Quiz {quiz.name} deleted successfully"), 200
        
@quiz_bp.route('/admin/quiz/<int:id>/question', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_quiz_questions(id):
    quiz = Quiz.query.get(id)
    if not quiz:
        return make_response(False, error_message="Quiz not found"), 404

    questions = quiz.questions.all()
    if not questions:
        return make_response(False, error_message="No question found"), 404

    question_list = []
    for question in questions:
        question_list.append({
            "id": question.id,
            "quiz_id": question.quiz_id,
            "quiz_name": question.quiz.name if question.quiz else None,
            "chapter_id": question.quiz.chapter_id if question.quiz else None,
            "chapter_name": question.quiz.chapter.name if question.quiz and question.quiz.chapter else None,
            "subject_id": question.quiz.chapter.subject_id if question.quiz and question.quiz.chapter else None,
            "subject_name": question.quiz.chapter.subject.name if question.quiz and question.quiz.chapter and question.quiz.chapter.subject else None,
            "question": question.question,
            "option1": question.option1,
            "option2": question.option2,
            "option3": question.option3,
            "option4": question.option4,
            "answer": question.answer,
            "marks": question.marks
        })

    return make_response(True, message="Question retrieved successfully", data=question_list), 200

@quiz_bp.route('/admin/quiz/search', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def search_quizzes():
    """Search quizzes by name, description, chapter name, or subject name (query param: text)"""
    text = request.args.get('text', '')
    if not text or len(text) < 3:
        return make_response(False, error_message="Search text must be at least 3 characters long"), 400
    quizzes = Quiz.query \
    .join(Quiz.chapter) \
    .join(Chapter.subject) \
    .options(joinedload(Quiz.chapter).joinedload(Chapter.subject)) \
    .filter(
        or_(
            Quiz.name.ilike(f'%{text}%'),
            Quiz.description.ilike(f'%{text}%'),
            Chapter.name.ilike(f'%{text}%'),
            Subject.name.ilike(f'%{text}%')
        )
    ).all()

    if not quizzes:
        return make_response(False, error_message="No quiz found"), 404

    quiz_list = []
    for quiz in quizzes:
        quiz_list.append({
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

    return make_response(True, message="Quiz retrieved successfully", data=quiz_list), 200

@quiz_bp.route('/admin/user-scores', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_all_user_scores():
    from app.models.score import Score
    from app.models.quiz import Quiz
    from app.models.chapter import Chapter
    from app.models.subject import Subject
    from app.models.user import User
    from app.models.user_profile import UserProfile
    scores = Score.query.order_by(Score.quiz_id).all()
    result = {}
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
        subject = Subject.query.get(chapter.subject_id) if chapter else None
        user = User.query.get(score.user_id)
        user_profile = UserProfile.query.filter_by(user_id=score.user_id).first() if user else None
        subject_name = subject.name if subject else 'Unknown Subject'
        chapter_name = chapter.name if chapter else 'Unknown Chapter'
        quiz_start = quiz.start_date.strftime('%d-%m-%Y') if quiz else ''
        if subject_name not in result:
            result[subject_name] = {}
        if chapter_name not in result[subject_name]:
            result[subject_name][chapter_name] = []
        result[subject_name][chapter_name].append({
            'user_id': user.id if user else None,
            'user_name': user.fullname if user else '',
            'user_email': user.email if user else '',
            'user_pic': user_profile.profile_picture if user_profile else None,
            'quiz_id': quiz.id if quiz else None,
            'quiz_name': quiz.name if quiz else '',
            'quiz_start_date': quiz_start,
            'quiz_start_dt': quiz.start_date if quiz else None,
            'total_questions': score.total_questions,
            'attempted_questions': score.attempted_questions,
            'unattempted_questions': score.unattempted_questions,
            'total_marks': score.total_marks,
            'total_score': score.total_score,
            'date_stamp_of_attempt': score.date_stamp_of_attempt.strftime('%d-%m-%Y') if score.date_stamp_of_attempt else None,
            'time_stamp_of_attempt': score.time_stamp_of_attempt.strftime('%H:%M:%S') if score.time_stamp_of_attempt else None,
            'time_stamp_of_submited': score.time_stamp_of_submited.strftime('%H:%M:%S') if score.time_stamp_of_submited else None
        })
    for subject in result.values():
        for chapter_scores in subject.values():
            chapter_scores.sort(key=lambda x: x['quiz_start_dt'] or '')
            for s in chapter_scores:
                if 'quiz_start_dt' in s:
                    del s['quiz_start_dt']
    return make_response(True, message="All user scores grouped by subject and chapter", data=result), 200

@quiz_bp.route('/admin/user-scores/search', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def search_user_scores():
    from app.models.score import Score
    from app.models.quiz import Quiz
    from app.models.chapter import Chapter
    from app.models.subject import Subject
    from app.models.user import User
    from app.models.user_profile import UserProfile
    text = request.args.get('text', '').strip().lower()
    scores = Score.query.order_by(Score.quiz_id).all()
    result = {}
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
        subject = Subject.query.get(chapter.subject_id) if chapter else None
        user = User.query.get(score.user_id)
        user_profile = UserProfile.query.filter_by(user_id=score.user_id).first() if user else None
        if text:
            if not (
                (user and (text in user.fullname.lower() or text in user.email.lower())) or
                (subject and text in subject.name.lower()) or
                (chapter and text in chapter.name.lower()) or
                (quiz and text in quiz.name.lower())
            ):
                continue
        subject_name = subject.name if subject else 'Unknown Subject'
        chapter_name = chapter.name if chapter else 'Unknown Chapter'
        quiz_start = quiz.start_date.strftime('%d-%m-%Y') if quiz else ''
        if subject_name not in result:
            result[subject_name] = {}
        if chapter_name not in result[subject_name]:
            result[subject_name][chapter_name] = []
        result[subject_name][chapter_name].append({
            'user_id': user.id if user else None,
            'user_name': user.fullname if user else '',
            'user_email': user.email if user else '',
            'user_pic': user_profile.profile_picture if user_profile else None,
            'quiz_id': quiz.id if quiz else None,
            'quiz_name': quiz.name if quiz else '',
            'quiz_start_date': quiz_start,
            'total_questions': score.total_questions,
            'attempted_questions': score.attempted_questions,
            'unattempted_questions': score.unattempted_questions,
            'total_marks': score.total_marks,
            'total_score': score.total_score,
            'date_stamp_of_attempt': score.date_stamp_of_attempt.strftime('%d-%m-%Y') if score.date_stamp_of_attempt else None,
            'time_stamp_of_attempt': score.time_stamp_of_attempt.strftime('%H:%M:%S') if score.time_stamp_of_attempt else None,
            'time_stamp_of_submited': score.time_stamp_of_submited.strftime('%H:%M:%S') if score.time_stamp_of_submited else None
        })
    for subject in result.values():
        for chapter_scores in subject.values():
            chapter_scores.sort(key=lambda x: x['quiz_start_date'] or '')
    return make_response(True, message="Filtered user scores", data=result), 200

@quiz_bp.route('/admin/user-scores/<int:user_id>', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_user_scores(user_id):
    from app.models.score import Score
    from app.models.quiz import Quiz
    from app.models.chapter import Chapter
    from app.models.subject import Subject
    from app.models.user import User
    from app.models.user_profile import UserProfile
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.quiz_id).all()
    result = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
        subject = Subject.query.get(chapter.subject_id) if chapter else None
        user = User.query.get(score.user_id)
        user_profile = UserProfile.query.filter_by(user_id=score.user_id).first() if user else None
        result.append({
            'user_id': user.id if user else None,
            'user_name': user.fullname if user else '',
            'user_email': user.email if user else '',
            'user_pic': user_profile.profile_picture if user_profile else None,
            'quiz_id': quiz.id if quiz else None,
            'quiz_name': quiz.name if quiz else '',
            'quiz_start_date': quiz.start_date.strftime('%d-%m-%Y') if quiz else '',
            'chapter_id': chapter.id if chapter else None,
            'chapter_name': chapter.name if chapter else '',
            'subject_id': subject.id if subject else None,
            'subject_name': subject.name if subject else '',
            'total_questions': score.total_questions,
            'attempted_questions': score.attempted_questions,
            'unattempted_questions': score.unattempted_questions,
            'total_marks': score.total_marks,
            'total_score': score.total_score,
            'date_stamp_of_attempt': score.date_stamp_of_attempt.strftime('%d-%m-%Y') if score.date_stamp_of_attempt else None,
            'time_stamp_of_attempt': score.time_stamp_of_attempt.strftime('%H:%M:%S') if score.time_stamp_of_attempt else None,
            'time_stamp_of_submited': score.time_stamp_of_submited.strftime('%H:%M:%S') if score.time_stamp_of_submited else None
        })
    return make_response(True, message="User scores", data=result), 200