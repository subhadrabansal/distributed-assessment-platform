from flask import Blueprint, request
from app.extensions import db
from app.models.notification import UserPreference
from app.common.utils import make_response
from app.common.jwt_helper import extract_user_info_from_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, time

user_settings_bp = Blueprint('user_settings_bp', __name__)

def parse_time_str(tstr):
    if isinstance(tstr, time):
        return tstr
    if isinstance(tstr, str):
        try:
            return datetime.strptime(tstr, "%H:%M").time()
        except Exception:
            return None
    return None

@user_settings_bp.route('/user/settings', methods=['GET'])
@jwt_required()
def get_user_settings():
    user_id, roles = extract_user_info_from_jwt()
    if not user_id:
        return make_response(False, error_message="Invalid user token"), 401
    
    setting = UserPreference.query.filter_by(user_id=user_id).first()
    if not setting:
        from datetime import time
        setting = UserPreference(
            user_id=user_id,
            reminder_time=time(9, 0),
            reminder_channel='email',
            report_format='html',
            receive_weekly=False,
            receive_monthly=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(setting)
        db.session.commit()
    data = {
        "reminder_time": setting.reminder_time.strftime('%H:%M') if setting.reminder_time else None,
        "reminder_channel": setting.reminder_channel,
        "report_format": setting.report_format,
        "receive_weekly": setting.receive_weekly,
        "receive_monthly": setting.receive_monthly
    }
    return make_response(True, data=data), 200

@user_settings_bp.route('/user/settings', methods=['PUT'])
@jwt_required()
def update_user_settings():
    user_id, roles = extract_user_info_from_jwt()
    if not user_id:
        return make_response(False, error_message="Invalid user token"), 401
    
    setting = UserPreference.query.filter_by(user_id=user_id).first()
    if not setting:
        from datetime import time
        setting = UserPreference(
            user_id=user_id,
            reminder_time=time(9, 0),
            reminder_channel='email',
            report_format='html',
            receive_weekly=False,
            receive_monthly=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(setting)
    data = request.get_json()
    setting.reminder_time = parse_time_str(data.get('reminder_time', setting.reminder_time))
    setting.reminder_channel = data.get('reminder_channel', setting.reminder_channel)
    setting.report_format = data.get('report_format', setting.report_format)
    setting.receive_weekly = data.get('receive_weekly', setting.receive_weekly)
    setting.receive_monthly = data.get('receive_monthly', setting.receive_monthly)
    setting.updated_at = datetime.utcnow()
    db.session.commit()
    
    from app.celery_tasks import update_celery_schedule
    update_celery_schedule()
    
    return make_response(True, message="User settings updated"), 200
