from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.common.utils import make_response
from app.common.quiz_status_manager import QuizStatusManager
from app.common.role_utils import roles_required
from app.common.enums import USER_ROLE

quiz_status_bp = Blueprint('quiz_status_bp', __name__)

@quiz_status_bp.route('/api/admin/quiz/update-statuses', methods=['POST'])
@jwt_required()
@roles_required(USER_ROLE[1])  
def update_quiz_statuses():
    """
    Admin endpoint to manually update all quiz statuses
    """
    try:
        result = QuizStatusManager.update_all_quiz_statuses(context='admin_manual')
        
        response_data = {
            'total_quizzes': result['total_quizzes'],
            'updated_count': result['updated_count'],
            'updates': result['updates'],
            'errors': result['errors']
        }
        
        if result['errors']:
            return make_response(
                success=True,
                message=f"Updated {result['updated_count']} quiz statuses with {len(result['errors'])} errors",
                data=response_data
            ), 200
        else:
            return make_response(
                success=True,
                message=f"Successfully updated {result['updated_count']} quiz statuses",
                data=response_data
            ), 200
            
    except Exception as e:
        return make_response(
            success=False,
            error_message=f"Failed to update quiz statuses: {str(e)}"
        ), 500

@quiz_status_bp.route('/api/admin/quiz/status-summary', methods=['GET'])
@jwt_required()
@roles_required(USER_ROLE[1])  
def get_quiz_status_summary():
    """
    Admin endpoint to get quiz status summary and health check
    """
    try:
        summary = QuizStatusManager.get_quiz_status_summary()
        
        if 'error' in summary:
            return make_response(
                success=False,
                error_message=summary['error']
            ), 500
        
        return make_response(
            success=True,
            message="Quiz status summary retrieved successfully",
            data=summary
        ), 200
        
    except Exception as e:
        return make_response(
            success=False,
            error_message=f"Failed to get status summary: {str(e)}"
        ), 500

@quiz_status_bp.route('/api/admin/quiz/<int:quiz_id>/update-status', methods=['POST'])
@jwt_required()
@roles_required(USER_ROLE[1])  
def update_single_quiz_status(quiz_id):
    """
    Admin endpoint to update status for a single quiz
    """
    try:
        result = QuizStatusManager.update_single_quiz_status(quiz_id, context='admin_single')
        
        if result['success']:
            return make_response(
                success=True,
                message=f"Quiz {quiz_id} status checked/updated",
                data=result
            ), 200
        else:
            return make_response(
                success=False,
                error_message=result['error']
            ), 400
            
    except Exception as e:
        return make_response(
            success=False,
            error_message=f"Failed to update quiz status: {str(e)}"
        ), 500
