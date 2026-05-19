from flask import Blueprint, jsonify
from app.common.utils import make_response
from app.common.jwt_helper import extract_user_info_from_jwt
from flask_jwt_extended import jwt_required
from app.common.reminder_service import ReminderService
from app.common.report_service import ReportService
import logging

logger = logging.getLogger(__name__)

admin_notifications_bp = Blueprint('admin_notifications_bp', __name__)

@admin_notifications_bp.route('/admin/notifications/send-daily-reminders', methods=['POST'])
@jwt_required()
def trigger_daily_reminders():
    """
    Manually trigger daily reminders for all users (bypasses scheduling)
    """
    user_id, roles = extract_user_info_from_jwt()
    if not user_id or 'admin' not in roles:
        return make_response(False, error_message="Admin access required"), 403
    
    try:

        result = ReminderService.send_daily_reminders_manual()
        
        logger.info(f"Admin {user_id} manually triggered daily reminders. Result: {result}")
        
        return make_response(True, message=f"Daily reminders sent! {result}"), 200
        
    except Exception as e:
        logger.error(f"Error triggering daily reminders: {str(e)}")
        return make_response(False, error_message=f"Failed to trigger daily reminders: {str(e)}"), 500

@admin_notifications_bp.route('/admin/notifications/send-monthly-reports', methods=['POST'])
@jwt_required()
def trigger_monthly_reports():
    """
    Manually trigger monthly reports for all users (bypasses scheduling)
    """
    user_id, roles = extract_user_info_from_jwt()
    if not user_id or 'admin' not in roles:
        return make_response(False, error_message="Admin access required"), 403
    
    try:
        result = ReportService.send_monthly_reports_manual()
        
        logger.info(f"Admin {user_id} manually triggered monthly reports. Result: {result}")
        
        return make_response(True, message=f"Monthly reports generated and sent! {result}"), 200
        
    except Exception as e:
        logger.error(f"Error triggering monthly reports: {str(e)}")
        return make_response(False, error_message=f"Failed to trigger monthly reports: {str(e)}"), 500
