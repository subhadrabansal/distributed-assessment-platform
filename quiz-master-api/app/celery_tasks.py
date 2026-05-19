from celery.schedules import crontab
from app.celery_app import celery
import logging

logger = logging.getLogger(__name__)

def update_celery_schedule():
    from app.models.notification import AdminNotificationSetting, UserPreference
    from app.models.user import User
    
    daily = AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first()
    monthly = AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first()
    
    beat_schedule = {}
    
    if daily and daily.reminder_time:
        user_prefs = UserPreference.query.filter(
            UserPreference.reminder_time.isnot(None),
            UserPreference.reminder_channel.in_(['email', 'gchat'])
        ).all()
        
        admin_time = daily.reminder_time
        unique_times = {admin_time}
        
        for user_pref in user_prefs:
            unique_times.add(user_pref.reminder_time)
        
        logger.info(f"Creating daily reminder schedule for {len(unique_times)} different times:")
        logger.info(f"Admin default time: {admin_time}")
        for time_obj in unique_times:
            if time_obj != admin_time:
                logger.info(f"User preference time: {time_obj}")
        
        for i, time_obj in enumerate(unique_times):
            beat_schedule[f'send_daily_reminders_{i}'] = {
                'task': 'app.celery_tasks.send_daily_reminders_at_time',
                'schedule': crontab(hour=time_obj.hour, minute=time_obj.minute),
                'args': [time_obj.hour, time_obj.minute]
            }
    
    if monthly and monthly.reminder_time and monthly.report_day_of_month:
        beat_schedule['send_monthly_reports'] = {
            'task': 'app.celery_tasks.send_monthly_reports',
            'schedule': crontab(
                hour=monthly.reminder_time.hour,
                minute=monthly.reminder_time.minute,
                day_of_month=monthly.report_day_of_month
            ),
        }
    
    celery.conf.beat_schedule = beat_schedule

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    update_celery_schedule()

@celery.task
def send_daily_reminders():
    """
    Send daily reminders to users via G-Chat (email) based on:
    1. Users who haven't visited recently
    2. New quizzes created that are relevant to them
    """
    from app.common.reminder_service import ReminderService
    return ReminderService.send_daily_reminders()

@celery.task
def send_daily_reminders_at_time(hour, minute):
    """
    Send daily reminders to users who have set this specific time preference
    """
    from app.common.reminder_service import ReminderService
    return ReminderService.send_daily_reminders_at_time(hour, minute)

@celery.task
def send_monthly_reports():
    """
    Generate and send monthly activity reports to all users
    """
    from app.common.report_service import ReportService
    return ReportService.send_monthly_reports()

@celery.task
def export_user_csv(user_id, export_record_id=None):
    """
    Export individual user's quiz data as CSV with enhanced details
    """
    from app.common.report_service import ReportService
    return ReportService.export_user_csv_enhanced(user_id, export_record_id)

@celery.task
def export_admin_csv(requested_by):
    """
    Export all users' quiz data as CSV for admin
    """
    from app.common.report_service import ReportService
    return ReportService.export_admin_csv(requested_by)
