from flask import Blueprint, request
from app.extensions import db
from app.models.notification import AdminNotificationSetting
from app.common.utils import make_response
from datetime import datetime, time

admin_settings_bp = Blueprint('admin_settings_bp', __name__)

def parse_time_str(tstr):
    if isinstance(tstr, time):
        return tstr
    if isinstance(tstr, str):
        try:
            return datetime.strptime(tstr, "%H:%M").time()
        except Exception:
            return None
    return None

@admin_settings_bp.route('/admin/settings', methods=['GET'])
def get_admin_settings():
    settings = AdminNotificationSetting.query.all()

    mapped = {s.setting_type: {
        "id": s.id,
        "setting_type": s.setting_type,
        "reminder_time": s.reminder_time.strftime('%H:%M') if s.reminder_time else None,
        "reminder_channel": s.reminder_channel,
        "report_format": s.report_format,
        "report_day_of_month": s.report_day_of_month,
        "report_channel": s.report_channel
    } for s in settings}

    if 'daily_reminder' not in mapped:
        mapped['daily_reminder'] = {
            "id": None,
            "setting_type": "daily_reminder",
            "reminder_time": "09:00",
            "reminder_channel": "email",
            "report_format": None,
            "report_day_of_month": None,
            "report_channel": None
        }
    if 'monthly_report' not in mapped:
        mapped['monthly_report'] = {
            "id": None,
            "setting_type": "monthly_report",
            "reminder_time": "09:00",
            "reminder_channel": None,
            "report_format": "html",
            "report_day_of_month": 1,
            "report_channel": "email"
        }
    return make_response(True, data=mapped), 200

@admin_settings_bp.route('/admin/settings/<setting_type>', methods=['PUT'])
def update_admin_setting(setting_type):
    setting = AdminNotificationSetting.query.filter_by(setting_type=setting_type).first()
    if not setting:
        return make_response(False, error_message="No admin setting found for this type."), 404
    data = request.get_json()
    setting.reminder_time = parse_time_str(data.get('reminder_time', setting.reminder_time))
    if setting_type == 'daily_reminder':
        setting.reminder_channel = data.get('reminder_channel', setting.reminder_channel)
    elif setting_type == 'monthly_report':
        setting.report_format = data.get('report_format', setting.report_format)
        setting.report_day_of_month = data.get('report_day_of_month', setting.report_day_of_month)
        setting.report_channel = data.get('report_channel', setting.report_channel)
    setting.updated_at = datetime.utcnow()
    db.session.commit()
    
    from app.celery_tasks import update_celery_schedule
    update_celery_schedule()
    return make_response(True, message="Admin setting updated"), 200
