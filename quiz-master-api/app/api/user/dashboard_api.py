from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.quiz import Quiz
from app.models.score import Score
import json
import logging

logger = logging.getLogger(__name__)

user_dashboard_bp = Blueprint('user_dashboard', __name__)

@user_dashboard_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_user_dashboard_stats():
    """Get user-specific dashboard statistics"""
    try:
        current_user_identity = get_jwt_identity()
        logger.info(f"JWT Identity: {current_user_identity} (type: {type(current_user_identity)})")
        
        # Parse JWT identity (it's a JSON string containing user data)
        user_id = None
        if isinstance(current_user_identity, str):
            identity_data = json.loads(current_user_identity)
            user_id = identity_data.get('id')
        
        logger.info(f"Extracted user_id: {user_id}")
        
        user = User.query.get(user_id)
        logger.info(f"User lookup result: {user}")
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get user-specific quiz statistics
        total_quizzes = Quiz.query.count()  # All available quizzes
        
        # Get user's quiz attempts/registrations - use user.id for database queries
        user_scores = Score.query.filter_by(user_id=user.id).all()
        user_quiz_ids = [score.quiz_id for score in user_scores]
        
        registered_quizzes = len(set(user_quiz_ids))  # Unique quizzes user has attempted
        
        # Calculate completed quizzes (user has submitted - has time_stamp_of_submited)
        completed_scores = [score for score in user_scores if score.time_stamp_of_submited is not None]
        completed_quiz_ids = set([score.quiz_id for score in completed_scores])
        completed_quizzes = len(completed_quiz_ids)
        
        # Calculate in-progress quizzes (started but not submitted yet)
        in_progress_scores = [score for score in user_scores if score.time_stamp_of_submited is None]
        in_progress_quiz_ids = set([score.quiz_id for score in in_progress_scores])
        in_progress_quizzes = len(in_progress_quiz_ids)
        
        # Calculate absent quizzes (registered but never attempted)
        # Since user has score records for all registered quizzes, absent = 0
        absent_quizzes = 0
        
        # User's performance metrics (only for completed quizzes with valid scores)
        if completed_scores:
            # Calculate percentage-based average for completed quizzes only
            total_percentage = 0
            valid_scores = 0
            
            for score in completed_scores:
                if score.total_marks and score.total_marks > 0:
                    percentage = (score.total_score / score.total_marks) * 100
                    total_percentage += percentage
                    valid_scores += 1
            
            average_score = total_percentage / valid_scores if valid_scores > 0 else 0
        else:
            average_score = 0
        
        stats = {
            'total_quizzes': total_quizzes,
            'registered_quizzes': registered_quizzes,
            'completed_quizzes': completed_quizzes,
            'in_progress_quizzes': in_progress_quizzes, 
            'absent_quizzes': absent_quizzes,  # Always 0 if user has score records
            'average_score': round(average_score, 1),  # Round to 1 decimal place
            'user_name': user.username
        }
        
        logger.info(f"User {user.id} ({user.email}) dashboard stats: {stats}")
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error fetching user dashboard stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch dashboard statistics'
        }), 500

@user_dashboard_bp.route('/dashboard/chart-data', methods=['GET'])
@jwt_required()
def get_user_chart_data():
    """Get user-specific chart data for dashboard analytics"""
    try:
        current_user_identity = get_jwt_identity()
        logger.info(f"JWT Identity: {current_user_identity} (type: {type(current_user_identity)})")
        
        # Parse JWT identity (it's a JSON string containing user data)
        user_id = None
        if isinstance(current_user_identity, str):
            identity_data = json.loads(current_user_identity)
            user_id = identity_data.get('id')
        
        logger.info(f"Extracted user_id: {user_id}")
        
        user = User.query.get(user_id)
        logger.info(f"User lookup result: {user}")
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get user's quiz attempts with details
        from app.models.quiz import Quiz
        from app.models.subject import Subject
        from app.models.chapter import Chapter
        
        user_scores = Score.query.filter_by(user_id=user.id).join(Quiz).all()
        
        # Performance over time (last 10 completed quizzes)
        completed_scores = [score for score in user_scores if score.time_stamp_of_submited is not None]
        completed_scores.sort(key=lambda x: x.time_stamp_of_submited)
        recent_scores = completed_scores[-10:] if len(completed_scores) > 10 else completed_scores
        
        performance_data = []
        for score in recent_scores:
            if score.total_marks and score.total_marks > 0:
                percentage = (score.total_score / score.total_marks) * 100
                performance_data.append({
                    'date': score.time_stamp_of_submited.strftime('%Y-%m-%d'),
                    'score': round(percentage, 1)
                })
        
        # Subject-wise performance
        subject_scores = {}
        for score in completed_scores:
            if score.total_marks and score.total_marks > 0:
                quiz = Quiz.query.get(score.quiz_id)
                if quiz and quiz.chapter:
                    chapter = Chapter.query.get(quiz.chapter.id)
                    if chapter and chapter.subject:
                        subject = Subject.query.get(chapter.subject.id)
                        if subject:
                            subject_name = subject.name
                            percentage = (score.total_score / score.total_marks) * 100
                            
                            if subject_name not in subject_scores:
                                subject_scores[subject_name] = []
                            subject_scores[subject_name].append(percentage)
        
        # Calculate average for each subject
        subjects_data = []
        for subject_name, scores in subject_scores.items():
            avg_score = sum(scores) / len(scores)
            subjects_data.append({
                'name': subject_name,
                'score': round(avg_score, 1)
            })
        
        # Score distribution
        score_ranges = {'0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}
        for score in completed_scores:
            if score.total_marks and score.total_marks > 0:
                percentage = (score.total_score / score.total_marks) * 100
                if percentage <= 20:
                    score_ranges['0-20'] += 1
                elif percentage <= 40:
                    score_ranges['21-40'] += 1
                elif percentage <= 60:
                    score_ranges['41-60'] += 1
                elif percentage <= 80:
                    score_ranges['61-80'] += 1
                else:
                    score_ranges['81-100'] += 1
        
        score_distribution = [
            {'range': range_name, 'count': count}
            for range_name, count in score_ranges.items()
        ]
        
        chart_data = {
            'performance': performance_data,
            'subjects': subjects_data,
            'scoreDistribution': score_distribution
        }
        
        logger.info(f"User {user.id} ({user.email}) chart data: {chart_data}")
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching user chart data: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch chart data'
        }), 500
