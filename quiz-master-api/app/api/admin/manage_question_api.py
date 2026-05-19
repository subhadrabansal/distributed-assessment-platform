from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject
from app.schemas.question_schema import QuestionRequestSchema, QuestionEditRequestSchema
from app.common.enums import QUIZ_STATUSES
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from flask_jwt_extended import jwt_required
from app.common.role_utils import roles_required
from app.common.enums import USER_ROLE
from app.common.utils import make_response
from app.extensions_redis import get_redis_client
import json

question_bp = Blueprint('question_bp', __name__)

@question_bp.route('/admin/question', methods=['GET', 'POST'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_or_add_questions():
    redis_client = get_redis_client()
    cache_key = 'questions:all'
    if request.method == 'GET':
        cached = redis_client.get(cache_key)
        if cached:
            return make_response(True, message="Questions retrieved successfully (cache)", data=json.loads(cached)), 200
        questions = Question.query.all()
        if not questions:
            return make_response(False, error_message="No question found"), 404
        question_list = []
        for question in questions:
            chapter = question.quiz.chapter if question.quiz and hasattr(question.quiz, 'chapter') else None
            subject = chapter.subject if chapter and hasattr(chapter, 'subject') else None
            question_list.append({
                "id": question.id,
                "quiz_id": question.quiz_id,
                "quiz_name": question.quiz.name if question.quiz else None,
                "chapter_id": chapter.id if chapter else None,
                "chapter_name": chapter.name if chapter else None,
                "subject_id": subject.id if subject else None,
                "subject_name": subject.name if subject else None,
                "question": question.question,
                "option1": question.option1,
                "option2": question.option2,
                "option3": question.option3,
                "option4": question.option4,
                "answer": question.answer,
                "marks": question.marks
            })
        redis_client.setex(cache_key, 300, json.dumps(question_list))
        return make_response(True, message="Questions retrieved successfully", data=question_list), 200

    # POST
    data = request.get_json()
    errors = QuestionRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    quiz_id = data.get('quiz_id')
    question_text = data.get('question')
    option1 = data.get('option1')
    option2 = data.get('option2')
    option3 = data.get('option3')
    option4 = data.get('option4')
    answer = data.get('answer')
    marks = data.get('marks')

    if Question.query.filter_by(quiz_id=quiz_id, question=question_text).first():
        current_app.logger.warning(f"Failed registration attempt for question: {question_text}, question already exists")
        return make_response(False, error_message=f"Question {question_text} already exists"), 400
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        current_app.logger.warning(f"Failed registration attempt for question: {question_text}, quiz with ID {quiz_id} not found")
        return make_response(False, error_message=f"Quiz with ID {quiz_id} not found"), 400
    if quiz.status != QUIZ_STATUSES[0]:
        current_app.logger.warning(f"Failed registration attempt for question: {question_text}, quiz with ID {quiz_id} is not in the {QUIZ_STATUSES[0]} state")
        return make_response(False, error_message=f"Quiz with ID {quiz_id} is not in the {QUIZ_STATUSES[0]} state"), 400

    new_question = Question(
        quiz_id=quiz_id,
        question=question_text,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        answer=answer,
        marks=marks
    )

    db.session.add(new_question)
    db.session.commit()

    current_app.logger.info(f"Question {new_question.question} registered successfully.")
    response_data = {
        "id": new_question.id,
        "quiz_id": new_question.quiz_id,
        "quiz_name": new_question.quiz.name if new_question.quiz else None,
        "chapter_id": new_question.quiz.chapter_id if new_question.quiz else None,
        "chapter_name": new_question.quiz.chapter.name if new_question.quiz and new_question.quiz.chapter else None,
        "subject_id": new_question.quiz.chapter.subject_id if new_question.quiz and new_question.quiz.chapter else None,
        "subject_name": new_question.quiz.chapter.subject.name if new_question.quiz and new_question.quiz.chapter else None,
        "question": new_question.question,
        "option1": new_question.option1,
        "option2": new_question.option2,
        "option3": new_question.option3,
        "option4": new_question.option4,
        "answer": new_question.answer,
        "marks": new_question.marks
    }
    redis_client.delete(cache_key)
    return make_response(True, message="Question registered successfully", data=response_data), 201

@question_bp.route('/admin/question/<int:id>', methods=['PUT'])
@jwt_required()
@roles_required(USER_ROLE[1])
def update_question(id):
    data = request.get_json()
    errors = QuestionRequestSchema().validate(data)
    if errors:
        return make_response(False, error_message=errors), 400
    quiz_id = data.get('quiz_id')
    question_text = data.get('question')
    option1 = data.get('option1')
    option2 = data.get('option2')
    option3 = data.get('option3')
    option4 = data.get('option4')
    answer = data.get('answer')
    marks = data.get('marks')

    question = Question.query.get(id)
    if not question:
        current_app.logger.warning(f"Failed to edit chapter, question with ID {id} not found")
        return make_response(False, error_message=f"Question with ID {id} not found"), 404

    existing_question = Question.query.filter_by(quiz_id=quiz_id, question=question_text).first()
    if existing_question and existing_question.id != id:
        current_app.logger.warning(f"Failed registration attempt for question: {question_text}, question already exists")
        return make_response(False, error_message=f"Question {question_text} already exists"), 400

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        current_app.logger.warning(f"Failed registration attempt for question: {question_text}, quiz with ID {quiz_id} not found")
        return make_response(False, error_message=f"Quiz with ID {quiz_id} not found"), 400
    if quiz.status != QUIZ_STATUSES[0]:
        current_app.logger.warning(f"Failed registration attempt for question: {question_text}, quiz with ID {quiz_id} is not in the {QUIZ_STATUSES[0]} state")
        return make_response(False, error_message=f"Quiz with ID {quiz_id} is not in the {QUIZ_STATUSES[0]} state"), 400

    question.quiz_id = quiz_id
    question.question = question_text
    question.option1 = option1
    question.option2 = option2
    question.option3 = option3
    question.option4 = option4
    question.answer = answer
    question.marks = marks

    db.session.commit()
    current_app.logger.info(f"Question {question.question} updated successfully.")
    response_data = {
        "id": question.id,
        "quiz_id": question.quiz_id,
        "quiz_name": question.quiz.name if question.quiz else None,
        "chapter_id": question.quiz.chapter_id if question.quiz else None,
        "chapter_name": question.quiz.chapter.name if question.quiz and question.quiz.chapter else None,
        "subject_id": question.quiz.chapter.subject_id if question.quiz and question.quiz.chapter else None,
        "subject_name": question.quiz.chapter.subject.name if question.quiz and question.quiz.chapter else None,
        "question": question.question,
        "option1": question.option1,
        "option2": question.option2,
        "option3": question.option3,
        "option4": question.option4,
        "answer": question.answer,
        "marks": question.marks
    }
    from app.extensions_redis import get_redis_client
    redis_client = get_redis_client()
    redis_client.delete('questions:all')
    return make_response(True, message="Question updated successfully", data=response_data), 200

@question_bp.route('/admin/question/<int:id>', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def get_question(id):
    question = Question.query.get(id)
    if not question:
        return make_response(False, error_message="Question not found"), 404

    question_data = {
        "id": question.id,
        "quiz_id": question.quiz_id,
        "quiz_name": question.quiz.name if question.quiz else None,
        "chapter_id": question.quiz.chapter_id if question.quiz else None,
        "chapter_name": question.quiz.chapter.name if question.quiz and question.quiz.chapter else None,
        "subject_id": question.quiz.chapter.subject_id if question.quiz and question.quiz.chapter else None,
        "subject_name": question.quiz.chapter.subject.name if question.quiz and question.quiz.chapter else None,
        "question": question.question,
        "option1": question.option1,
        "option2": question.option2,
        "option3": question.option3,
        "option4": question.option4,
        "answer": question.answer,
        "marks": question.marks
    }

    return make_response(True, message="Question retrieved successfully", data=question_data), 200    

@question_bp.route('/admin/question/<int:id>', methods=['DELETE'])
@jwt_required()
@roles_required(USER_ROLE[1])
def delete_question(id):
    question = Question.query.get(id)
    if not question:
        return make_response(False, error_message="Question not found"), 404
    quiz = Quiz.query.get(question.quiz_id)
    if quiz.status != QUIZ_STATUSES[0]:
        return make_response(False, error_message=f"Question cannot be deleted because it is not in the {QUIZ_STATUSES[0]} state."), 400
    else:
        db.session.delete(question)
        db.session.commit()
        redis_client = get_redis_client()
        redis_client.delete('questions:all')
        current_app.logger.info(f"Question {question.question} deleted successfully.")
        return make_response(True, message="Question deleted successfully"), 200

@question_bp.route('/admin/question/search', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])
def search_questions():
    """ Search questions by text (query param: text) """
    text = request.args.get('text', '')
    if not text or len(text) < 2:
        return make_response(False, error_message="Search text must be at least 2 characters long"), 400
    questions = Question.query \
    .join(Question.quiz) \
    .join(Quiz.chapter) \
    .join(Chapter.subject) \
    .filter(
        or_(
            Question.question.ilike(f'%{text}%'),
            Quiz.name.ilike(f'%{text}%'),
            Chapter.name.ilike(f'%{text}%'),
            Subject.name.ilike(f'%{text}%')
        )
    ).all()

    if not questions:
        return make_response(False, error_message="No questions found matching the search criteria"), 404
    question_list = []
    for question in questions:
        question_list.append({
            "id": question.id,
            "quiz_id": question.quiz_id,
            "quiz_name": question.quiz.name if question.quiz else None,
            "chapter_id": question.quiz.chapter_id if question.quiz else None,
            "chapter_name": question.quiz.chapter.name if question.quiz and question.quiz.chapter else None,
            "subject_id": question.quiz.chapter.subject_id if question.quiz and question.quiz.chapter else None,
            "subject_name": question.quiz.chapter.subject.name if question.quiz and question.quiz.chapter else None,
            "question": question.question,
            "option1": question.option1,
            "option2": question.option2,
            "option3": question.option3,
            "option4": question.option4,
            "answer": question.answer,
            "marks": question.marks
        })
    return make_response(True, message="Questions retrieved successfully", data=question_list), 200

@question_bp.route('/admin/quiz/<int:quiz_id>/question', methods=['GET'])
def get_questions_by_quiz(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        return make_response(False, error_message="No questions found for this quiz"), 404
    question_list = []
    for question in questions:
        chapter = question.quiz.chapter if question.quiz and hasattr(question.quiz, 'chapter') else None
        subject = chapter.subject if chapter and hasattr(chapter, 'subject') else None
        question_list.append({
            "id": question.id,
            "quiz_id": question.quiz_id,
            "quiz_name": question.quiz.name if question.quiz else None,
            "chapter_id": chapter.id if chapter else None,
            "chapter_name": chapter.name if chapter else None,
            "subject_id": subject.id if subject else None,
            "subject_name": subject.name if subject else None,
            "question": question.question,
            "option1": question.option1,
            "option2": question.option2,
            "option3": question.option3,
            "option4": question.option4,
            "answer": question.answer,
            "marks": question.marks
        })
    return make_response(True, message="Questions retrieved successfully", data=question_list), 200


