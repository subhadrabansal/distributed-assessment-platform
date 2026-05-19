from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject
from app.models.score import Score
from app.models.question import Question
from app.models.user import User  # Ensure this import is present
from app.models.answer import Answer
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.common.enums import QUIZ_STATUSES, USER_ROLE
from app.common.jwt_helper import extract_user_info_from_jwt
from app.common.utils import make_response
import json
import logging

logger = logging.getLogger(__name__)

quiz_registration_bp = Blueprint('quiz_registration_bp', __name__)

@quiz_registration_bp.route('/user/quiz/ongoing-unregistered', methods=['GET'])
@jwt_required()
def get_ongoing_unregistered_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    now = datetime.now()
    ongoing_quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        # Quiz.status == QUIZ_STATUSES[1],  # Assuming QUIZ_STATUS[1] is for ongoing quizzes
        Quiz.start_date <= now,
        Quiz.end_date >= now
    ).all()
    registered_quiz_ids = set(row.quiz_id for row in Score.query.filter_by(user_id=user_id).filter(Score.quiz_registration_date.isnot(None)).all())
    unregistered_quizzes = [q for q in ongoing_quizzes if q.id not in registered_quiz_ids]
    quiz_list = []
    for quiz in unregistered_quizzes:
        questions = quiz.questions.all()
        total_marks = sum(q.marks for q in questions)
        quiz_list.append({
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "name": quiz.name,
            "description": quiz.description,
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            "start_date": quiz.start_date.strftime('%d-%m-%Y'),
            "end_date": quiz.end_date.strftime('%d-%m-%Y'),
            "duration": quiz.duration,
            "questions": len(questions),
            "total_marks": total_marks
        })
    quiz_list.sort(key=lambda x: (x['subject_name'] or '', x['chapter_name'] or '', datetime.strptime(x['start_date'], '%d-%m-%Y')))
    return make_response(True, message="Ongoing unregistered quizzes", data=quiz_list), 200

@quiz_registration_bp.route('/user/quiz/upcoming-unregistered', methods=['GET'])
@jwt_required()
def get_upcoming_unregistered_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    now = datetime.now()
    upcoming_quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        #Quiz.status == QUIZ_STATUSES[0],  # Assuming QUIZ_STATUSES[0] is for upcoming quizzes
        Quiz.start_date > now
    ).all()
    registered_quiz_ids = set(row.quiz_id for row in Score.query.filter_by(user_id=user_id).filter(Score.quiz_registration_date.isnot(None)).all())
    unregistered_quizzes = [q for q in upcoming_quizzes if q.id not in registered_quiz_ids]
    quiz_list = []
    for quiz in unregistered_quizzes:
        questions = quiz.questions.all()
        total_marks = sum(q.marks for q in questions)
        quiz_list.append({
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "name": quiz.name,
            "description": quiz.description,
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            "start_date": quiz.start_date.strftime('%d-%m-%Y'),
            "end_date": quiz.end_date.strftime('%d-%m-%Y'),
            "duration": quiz.duration,
            "questions": len(questions),
            "total_marks": total_marks
        })
    quiz_list.sort(key=lambda x: (x['subject_name'] or '', x['chapter_name'] or '', datetime.strptime(x['start_date'], '%d-%m-%Y')))
    return make_response(True, message="Upcoming unregistered quizzes", data=quiz_list), 200

@quiz_registration_bp.route('/user/quiz/register', methods=['POST'])
@jwt_required()
def register_user_for_quiz():
    user_id, _ = extract_user_info_from_jwt()
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    if not quiz_id:
        return make_response(False, error_message='quiz_id is required'), 400
    existing = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing:
        return make_response(False, error_message='Already registered for this quiz'), 400
    new_score = Score(user_id=user_id, quiz_id=quiz_id)
    db.session.add(new_score)
    db.session.commit()
    return make_response(True, message='Registered for quiz successfully', data={
        'user_id': user_id,
        'quiz_id': quiz_id,
        'quiz_registration_date': new_score.quiz_registration_date.strftime('%d-%m-%Y %H:%M:%S')
    }), 201

@quiz_registration_bp.route('/user/quiz/registered-unattempted', methods=['GET'])
@jwt_required()
def get_registered_unattempted_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    now = datetime.now()
    scores = Score.query.filter_by(user_id=user_id).filter(Score.time_stamp_of_attempt == None).all()
    quiz_list = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        questions = quiz.questions.all()
        total_marks = sum(q.marks for q in questions)
        quiz_list.append({
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "name": quiz.name,
            "description": quiz.description,
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            "start_date": quiz.start_date.strftime('%d-%m-%Y'),
            "end_date": quiz.end_date.strftime('%d-%m-%Y'),
            "duration": quiz.duration,
            "questions": len(questions),
            "total_marks": total_marks,
            "quiz_registration_date": score.quiz_registration_date.strftime('%d-%m-%Y %H:%M:%S') if score.quiz_registration_date else None
        })
    quiz_list.sort(key=lambda x: (x['subject_name'] or '', x['chapter_name'] or '', datetime.strptime(x['start_date'], '%d-%m-%Y')))
    return make_response(True, message="Registered but unattempted quizzes", data=quiz_list), 200

@quiz_registration_bp.route('/user/quiz/registered', methods=['GET'])
@jwt_required()
def get_registered_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    scores = Score.query.filter_by(user_id=user_id).filter(Score.time_stamp_of_submited == None).all()
    quiz_list = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        questions = quiz.questions.all()
        total_marks = sum(q.marks for q in questions)
        quiz_list.append({
            # Quiz details
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "name": quiz.name,
            "description": quiz.description,
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            "start_date": quiz.start_date.strftime('%d-%m-%Y'),
            "end_date": quiz.end_date.strftime('%d-%m-%Y'),
            "duration": quiz.duration,
            "questions": len(questions),
            "total_marks": total_marks,
            # Score details
            "quiz_registration_date": score.quiz_registration_date.strftime('%d-%m-%Y %H:%M:%S') if score.quiz_registration_date else None,
            "date_stamp_of_attempt": score.date_stamp_of_attempt.strftime('%d-%m-%Y') if score.date_stamp_of_attempt else None,
            "time_stamp_of_attempt": score.time_stamp_of_attempt.strftime('%H:%M:%S') if score.time_stamp_of_attempt else None,
            "time_stamp_of_submited": score.time_stamp_of_submited.strftime('%H:%M:%S') if score.time_stamp_of_submited else None,
            "total_questions": score.total_questions,
            "attempted_questions": score.attempted_questions,
            "unattempted_questions": score.unattempted_questions,
            "total_score": score.total_score
        })
    quiz_list.sort(key=lambda x: (x['subject_name'] or '', x['chapter_name'] or '', datetime.strptime(x['start_date'], '%d-%m-%Y')))
    return make_response(True, message="All registered quizzes with details", data=quiz_list), 200

@quiz_registration_bp.route('/user/quiz/ongoing-unregistered/search', methods=['GET'])
@jwt_required()
def search_ongoing_unregistered_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    now = datetime.now()
    text = request.args.get('text', '').strip().lower()
    ongoing_quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        Quiz.start_date <= now,
        Quiz.end_date >= now
    ).all()
    registered_quiz_ids = set(row.quiz_id for row in Score.query.filter_by(user_id=user_id).filter(Score.quiz_registration_date.isnot(None)).all())
    unregistered_quizzes = [q for q in ongoing_quizzes if q.id not in registered_quiz_ids]
    filtered = filter_and_format_quizzes(unregistered_quizzes, text)
    return make_response(True, message="Filtered ongoing unregistered quizzes", data=filtered), 200

@quiz_registration_bp.route('/user/quiz/upcoming-unregistered/search', methods=['GET'])
@jwt_required()
def search_upcoming_unregistered_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    now = datetime.now()
    text = request.args.get('text', '').strip().lower()
    upcoming_quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        Quiz.status == QUIZ_STATUSES[0],
        Quiz.start_date > now
    ).all()
    registered_quiz_ids = set(row.quiz_id for row in Score.query.filter_by(user_id=user_id).filter(Score.quiz_registration_date.isnot(None)).all())
    unregistered_quizzes = [q for q in upcoming_quizzes if q.id not in registered_quiz_ids]
    filtered = filter_and_format_quizzes(unregistered_quizzes, text)
    return make_response(True, message="Filtered upcoming unregistered quizzes", data=filtered), 200

@quiz_registration_bp.route('/user/quiz/registered/search', methods=['GET'])
@jwt_required()
def search_registered_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    text = request.args.get('text', '').strip().lower()
    scores = Score.query.filter_by(user_id=user_id).all()
    quiz_ids = [score.quiz_id for score in scores]
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all()
    score_map = {score.quiz_id: score for score in scores}
    filtered = filter_and_format_quizzes(quizzes, text, include_score_fields=True, score_map=score_map)
    return make_response(True, message="Filtered registered quizzes", data=filtered), 200

@quiz_registration_bp.route('/user/quiz/completed/search', methods=['GET'])
@jwt_required()
def search_completed_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    text = request.args.get('text', '').strip().lower()
    scores = Score.query.filter_by(user_id=user_id).filter(Score.time_stamp_of_attempt != None).all()
    quiz_ids = [score.quiz_id for score in scores]
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all()
    score_map = {score.quiz_id: score for score in scores}
    filtered = filter_and_format_quizzes(quizzes, text, include_score_fields=True, score_map=score_map)
    return make_response(True, message="Filtered completed quizzes", data=filtered), 200

@quiz_registration_bp.route('/user/quiz/completed', methods=['GET'])
@jwt_required()
def get_completed_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    scores = Score.query.filter_by(user_id=user_id).filter(Score.time_stamp_of_attempt != None).all()
    quiz_list = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        questions = quiz.questions.all()
        total_marks = sum(q.marks for q in questions)
        quiz_list.append({
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "name": quiz.name,
            "description": quiz.description,
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            "start_date": quiz.start_date.strftime('%d-%m-%Y'),
            "end_date": quiz.end_date.strftime('%d-%m-%Y'),
            "duration": quiz.duration,
            "questions": len(questions),
            "total_marks": total_marks,
            "quiz_registration_date": score.quiz_registration_date.strftime('%d-%m-%Y %H:%M:%S') if score.quiz_registration_date else None,
            "date_stamp_of_attempt": score.date_stamp_of_attempt.strftime('%d-%m-%Y') if score.date_stamp_of_attempt else None,
            "time_stamp_of_attempt": score.time_stamp_of_attempt.strftime('%H:%M:%S') if score.time_stamp_of_attempt else None,
            "time_stamp_of_submited": score.time_stamp_of_submited.strftime('%H:%M:%S') if score.time_stamp_of_submited else None,
            "total_questions": score.total_questions,
            "attempted_questions": score.attempted_questions,
            "unattempted_questions": score.unattempted_questions,
            "total_score": score.total_score
        })
    quiz_list.sort(key=lambda x: (x['subject_name'] or '', x['chapter_name'] or '', datetime.strptime(x['start_date'], '%d-%m-%Y')))
    return make_response(True, message="Completed quizzes", data=quiz_list), 200

@quiz_registration_bp.route('/user/quiz/absent', methods=['GET'])
@jwt_required()
def get_absent_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    now = datetime.now()
    scores = Score.query.filter_by(user_id=user_id).filter(Score.time_stamp_of_attempt == None).all()
    quiz_list = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        if quiz.end_date >= now:
            continue  
        questions = quiz.questions.all()
        total_marks = sum(q.marks for q in questions)
        quiz_list.append({
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "name": quiz.name,
            "description": quiz.description,
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            "start_date": quiz.start_date.strftime('%d-%m-%Y'),
            "end_date": quiz.end_date.strftime('%d-%m-%Y'),
            "duration": quiz.duration,
            "questions": len(questions),
            "total_marks": total_marks,
            "quiz_registration_date": score.quiz_registration_date.strftime('%d-%m-%Y %H:%M:%S') if score.quiz_registration_date else None
        })
    quiz_list.sort(key=lambda x: (x['subject_name'] or '', x['chapter_name'] or '', datetime.strptime(x['start_date'], '%d-%m-%Y')))
    return make_response(True, message="Absent quizzes", data=quiz_list), 200

@quiz_registration_bp.route('/user/quiz/attempt/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_attempt(quiz_id):
    user_id, _ = extract_user_info_from_jwt()
    score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not score:
        return make_response(False, error_message='Not registered for this quiz'), 404
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return make_response(False, error_message='Quiz not found'), 404
    questions = []
    for q in quiz.questions:
        options = []
        if hasattr(q, 'option1') and q.option1 is not None:
            options.append({"id": 1, "text": q.option1})
        if hasattr(q, 'option2') and q.option2 is not None:
            options.append({"id": 2, "text": q.option2})
        if hasattr(q, 'option3') and q.option3 is not None:
            options.append({"id": 3, "text": q.option3})
        if hasattr(q, 'option4') and q.option4 is not None:
            options.append({"id": 4, "text": q.option4})
        questions.append({
            "id": q.id,
            "text": q.question,
            "options": options
        })
    prev_answers = score.answers if hasattr(score, 'answers') and score.answers else {}
    from datetime import datetime, timedelta
    now = datetime.now()
    if score.date_stamp_of_attempt and score.time_stamp_of_attempt:
        attempt_datetime = datetime.combine(score.date_stamp_of_attempt, score.time_stamp_of_attempt)
        elapsed = (now - attempt_datetime).total_seconds()
        time_left = max(0, quiz.duration * 60 - int(elapsed))
    else:
        score.date_stamp_of_attempt = now.date()
        score.time_stamp_of_attempt = now.time()
        db.session.commit()
        time_left = quiz.duration * 60
    user_obj = User.query.get(score.user_id)
    user = {
        "name": user_obj.name if user_obj else "",
        "email": user_obj.email if user_obj else "",
        "pic": getattr(user_obj, 'pic', '') if user_obj else ""
    }
    return make_response(True, data={
        "user": user,
        "quiz": {
            "id": quiz.id,
            "name": quiz.name,
            "duration": quiz.duration,
            "total_marks": sum(q.marks for q in quiz.questions),
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None
        },
        "questions": questions,
        "answers": prev_answers,
        "time_left": time_left
    }), 200

@quiz_registration_bp.route('/user/quiz/attempt', methods=['POST'])
@jwt_required()
def get_quiz_attempt_post():
    user_id, _ = extract_user_info_from_jwt()
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    if not quiz_id:
        return make_response(False, error_message='quiz_id is required'), 400
    score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not score:
        return make_response(False, error_message='Not registered for this quiz'), 404
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return make_response(False, error_message='Quiz not found'), 404
    questions = []
    for q in quiz.questions:
        options = []
        if hasattr(q, 'option1') and q.option1 is not None:
            options.append({"id": 1, "text": q.option1})
        if hasattr(q, 'option2') and q.option2 is not None:
            options.append({"id": 2, "text": q.option2})
        if hasattr(q, 'option3') and q.option3 is not None:
            options.append({"id": 3, "text": q.option3})
        if hasattr(q, 'option4') and q.option4 is not None:
            options.append({"id": 4, "text": q.option4})
        questions.append({
            "id": q.id,
            "text": q.question,
            "options": options
        })
    prev_answers = score.answers if hasattr(score, 'answers') and score.answers else {}
    from datetime import datetime, timedelta
    now = datetime.now()
    if score.date_stamp_of_attempt and score.time_stamp_of_attempt:
        attempt_datetime = datetime.combine(score.date_stamp_of_attempt, score.time_stamp_of_attempt)
        elapsed = (now - attempt_datetime).total_seconds()
        time_left = max(0, quiz.duration * 60 - int(elapsed))
    else:
        score.date_stamp_of_attempt = now.date()
        score.time_stamp_of_attempt = now.time()
        db.session.commit()
        time_left = quiz.duration * 60
    user_obj = User.query.get(score.user_id)
    user = {
        "name": user_obj.fullname if user_obj else "",
        "email": user_obj.email if user_obj else "",
        "pic": user_obj.user_profile.profile_picture if user_obj and hasattr(user_obj, 'user_profile') else ""
    }
    return make_response(True, data={
        "user": user,
        "quiz": {
            "id": quiz.id,
            "name": quiz.name,
            "duration": quiz.duration,
            "total_marks": sum(q.marks for q in quiz.questions),
            "chapter_name": quiz.chapter.name if quiz.chapter else None,
            "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None
        },
        "questions": questions,
        "answers": prev_answers,
        "time_left": time_left
    }), 200

@quiz_registration_bp.route('/user/quiz/answer', methods=['POST'])
@jwt_required()
def save_user_answer():
    user_id, _ = extract_user_info_from_jwt()
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    question_id = data.get('question_id')
    user_answer = data.get('user_answer')
    if not (quiz_id and question_id):
        return make_response(False, error_message='quiz_id and question_id are required'), 400
    answer = Answer.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).first()
    if not answer:
        answer = Answer(user_id=user_id, quiz_id=quiz_id, question_id=question_id)
        db.session.add(answer)
    answer.user_answer = user_answer
    answer.updated_at = datetime.now()
    db.session.commit()
    return make_response(True, message='Answer saved'), 200

@quiz_registration_bp.route('/user/quiz/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    user_id, _ = extract_user_info_from_jwt()
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not score:
        return make_response(False, error_message='Not registered for this quiz'), 404
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return make_response(False, error_message='Quiz not found'), 404
    questions_list = quiz.questions.all()
    total_questions = len(questions_list)
    answers = {a.question_id: a.user_answer for a in Answer.query.filter_by(user_id=user_id, quiz_id=quiz_id).all()}
    attempted = len([v for v in answers.values() if v is not None])
    unattempted = total_questions - attempted
    logger.info(f"[DEBUG] Submitting quiz: user_id={user_id}, quiz_id={quiz_id}, total_questions={total_questions}, attempted={attempted}, unattempted={unattempted}")
    total_score = 0
    for q in questions_list:
        ans = answers.get(q.id)
        logger.info(f"[DEBUG] Scoring: question_id={q.id}, user_answer={ans}, correct_answer={q.answer}, marks={q.marks}")
        answer_obj = Answer.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=q.id).first()
        if answer_obj:
            logger.info(f"[DEBUG] Updating answer object: {answer_obj}, {answer_obj.user_answer}, {answer_obj.correct_answer}, {answer_obj.question_marks}")
            answer_obj.correct_answer = int(q.answer) if q.answer is not None else None
            answer_obj.question_marks = q.marks
            logger.info(f"[DEBUG] question_answer=answer{q.answer}={ans}")
            if ans is not None and int(ans) == int(q.answer):
                logger.info(f"[DEBUG] Correct answer for question_answer=answer{q.answer}={ans}, marks awarded={q.marks}, {ans.strip() if isinstance(ans, str) else ans}")
                total_score += q.marks
    score.total_questions = total_questions
    score.attempted_questions = attempted
    score.unattempted_questions = unattempted
    score.total_marks = sum(q.marks for q in questions_list)
    score.total_score = total_score
    logger.info(f"[DEBUG] Before commit: user_id={user_id}, quiz_id={quiz_id}, total_score={score.total_score}, attempted={score.attempted_questions}, unattempted={score.unattempted_questions}, total_marks={score.total_marks}")
    score.time_stamp_of_submited = datetime.now().time()
    db.session.commit()
    logger.info(f"[DEBUG] After commit: user_id={user_id}, quiz_id={quiz_id}, total_score={score.total_score}")
    return make_response(True, message='Quiz submitted successfully'), 200

@quiz_registration_bp.route('/user/quiz/score/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_score(quiz_id):
    user_id, _ = extract_user_info_from_jwt()
    score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not score:
        return make_response(False, error_message='Score not found'), 404
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return make_response(False, error_message='Quiz not found'), 404
    user_obj = User.query.get(user_id)
    user_profile = getattr(user_obj, 'user_profile', None)
    logger.info(f"User object for certificate: id={user_id}, fullname={getattr(user_obj, 'fullname', None)}, email={getattr(user_obj, 'email', None)}, profile_picture={getattr(user_profile, 'profile_picture', None)}")
    user_data = {
        "name": user_obj.fullname if user_obj and getattr(user_obj, 'fullname', None) else "Anonymous",
        "pic": user_profile.profile_picture if user_profile and getattr(user_profile, 'profile_picture', None) else None,
        "email": user_obj.email if user_obj and getattr(user_obj, 'email', None) else ""
    }
    quiz_data = {
        "name": quiz.name if quiz else "",
        "subject_name": quiz.chapter.subject.name if quiz and quiz.chapter and quiz.chapter.subject else "",
        "chapter_name": quiz.chapter.name if quiz and quiz.chapter else "",
        "total_marks": sum(q.marks for q in quiz.questions) if quiz and quiz.questions else 0
    }
    score_data = {
        "total_questions": score.total_questions if score and hasattr(score, 'total_questions') else 0,
        "attempted_questions": score.attempted_questions if score and hasattr(score, 'attempted_questions') else 0,
        "unattempted_questions": score.unattempted_questions if score and hasattr(score, 'unattempted_questions') else 0,
        "total_score": score.total_score if score and hasattr(score, 'total_score') else 0,
        "date": score.date_stamp_of_attempt.strftime('%d %b %Y') if score and getattr(score, 'date_stamp_of_attempt', None) else '',
        "time": score.time_stamp_of_submited.strftime('%H:%M:%S') if score and getattr(score, 'time_stamp_of_submited', None) else ''
    }
    return make_response(True, data={
        "user": user_data,
        "quiz": quiz_data,
        "score": score_data
    }), 200

@quiz_registration_bp.route('/user/quiz/score', methods=['POST'])
@jwt_required()
def get_quiz_score_post():
    data = request.get_json()
    identity = get_jwt_identity()
    if not identity:
        return make_response(False, error_message='User not authenticated'), 401
    user_id, _ = extract_user_info_from_jwt()
    logger.info(f"Extracted user_id={user_id} from JWT")
    if not user_id:
        return make_response(False, error_message='User not authenticated'), 401
    quiz_id = data.get('quiz_id')
    if not quiz_id:
        return make_response(False, error_message='quiz_id is required'), 400
    logger.info(f"Fetching score for user_id={user_id}, quiz_id={quiz_id}")
    score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not score:
        return make_response(False, error_message='Score not found'), 404
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return make_response(False, error_message='Quiz not found'), 404
    user = User.query.get(user_id)
    logger.info(f"User object for certificate: id={user_id}, {user.fullname}")
    user_data = {
        "name": user.fullname,
        "pic": user.user_profile.profile_picture,
        "email": user.email
    }
    logger.info(f"User data for certificate: {user_data}")
    quiz_data = {
        "name": quiz.name if quiz else "",
        "subject_name": quiz.chapter.subject.name if quiz and quiz.chapter and quiz.chapter.subject else "",
        "chapter_name": quiz.chapter.name if quiz and quiz.chapter else "",
        "total_marks": sum(q.marks for q in quiz.questions) if quiz and quiz.questions else 0
    }
    score_data = {
        "total_questions": score.total_questions if score and hasattr(score, 'total_questions') else 0,
        "attempted_questions": score.attempted_questions if score and hasattr(score, 'attempted_questions') else 0,
        "unattempted_questions": score.unattempted_questions if score and hasattr(score, 'unattempted_questions') else 0,
        "total_score": score.total_score if score and hasattr(score, 'total_score') else 0,
        "date": score.date_stamp_of_attempt.strftime('%d %b %Y') if score and getattr(score, 'date_stamp_of_attempt', None) else '',
        "time": score.time_stamp_of_submited.strftime('%H:%M:%S') if score and getattr(score, 'time_stamp_of_submited', None) else ''
    }
    return make_response(True, data={
        "user": user_data,
        "quiz": quiz_data,
        "score": score_data
    }), 200

@quiz_registration_bp.route('/user/quiz/absent/search', methods=['GET'])
@jwt_required()
def search_absent_quizzes():
    user_id, _ = extract_user_info_from_jwt()
    now = datetime.now()
    text = request.args.get('text', '').strip().lower()
    scores = Score.query.filter_by(user_id=user_id).filter(Score.time_stamp_of_attempt == None).all()
    quiz_ids = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue
        if quiz.end_date >= now:
            continue
        quiz_ids.append(quiz.id)
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all() if quiz_ids else []
    score_map = {score.quiz_id: score for score in scores if score.quiz_id in quiz_ids}
    filtered = filter_and_format_quizzes(quizzes, text, include_score_fields=True, score_map=score_map)
    return make_response(True, message="Filtered absent quizzes", data=filtered), 200

def filter_and_format_quizzes(quizzes, search_text, include_score_fields=False, score_map=None):
    filtered = []
    for quiz in quizzes:
        quiz_name = (quiz.name or '').lower()
        chapter_name = (quiz.chapter.name if quiz.chapter else '').lower()
        subject_name = (quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else '').lower()
        if search_text in quiz_name or search_text in chapter_name or search_text in subject_name:
            questions = quiz.questions.all()
            total_marks = sum(q.marks for q in questions)
            quiz_dict = {
                "id": quiz.id,
                "chapter_id": quiz.chapter_id,
                "name": quiz.name,
                "description": quiz.description,
                "chapter_name": quiz.chapter.name if quiz.chapter else None,
                "subject_id": quiz.chapter.subject_id if quiz.chapter else None,
                "subject_name": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
                "start_date": quiz.start_date.strftime('%d-%m-%Y'),
                "end_date": quiz.end_date.strftime('%d-%m-%Y'),
                "duration": quiz.duration,
                "questions": len(questions),
                "total_marks": total_marks
            }
            if include_score_fields and score_map:
                score = score_map.get(quiz.id)
                if score:
                    quiz_dict.update({
                        "quiz_registration_date": score.quiz_registration_date.strftime('%d-%m-%Y %H:%M:%S') if score.quiz_registration_date else None,
                        "date_stamp_of_attempt": score.date_stamp_of_attempt.strftime('%d-%m-%Y') if score.date_stamp_of_attempt else None,
                        "time_stamp_of_attempt": score.time_stamp_of_attempt.strftime('%H:%M:%S') if score.time_stamp_of_attempt else None,
                        "time_stamp_of_submited": score.time_stamp_of_submited.strftime('%H:%M:%S') if score.time_stamp_of_submited else None,
                        "total_questions": score.total_questions,
                        "attempted_questions": score.attempted_questions,
                        "unattempted_questions": score.unattempted_questions,
                        "total_score": score.total_score
                    })
            filtered.append(quiz_dict)
    filtered.sort(key=lambda x: (x['subject_name'] or '', x['chapter_name'] or '', datetime.strptime(x['start_date'], '%d-%m-%Y')))
    return filtered


