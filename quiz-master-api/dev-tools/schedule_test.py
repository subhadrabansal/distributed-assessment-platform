#!/usr/bin/env python3
"""
Test Celery schedule by temporarily setting tasks to run in 2 minutes
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.notification import AdminNotificationSetting
from datetime import datetime, time, timedelta

def set_test_schedule():
    """Set tasks to run in 2 minutes for testing"""
    app = create_app()
    
    with app.app_context():
        test_time = datetime.now() + timedelta(minutes=2)
        test_hour = test_time.hour
        test_minute = test_time.minute
        
        print(f"🔧 Setting test schedule for {test_hour:02d}:{test_minute:02d}")
        
        daily = AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first()
        if daily:
            daily.reminder_time = time(test_hour, test_minute)
        
        monthly = AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first()
        if monthly:
            monthly.reminder_time = time(test_hour, test_minute)
            monthly.report_day_of_month = datetime.now().day
        
        from app.extensions import db
        db.session.commit()
        
        print(f"✅ Test schedule set:")
        print(f"   Daily reminders: {test_hour:02d}:{test_minute:02d}")
        print(f"   Monthly reports: {test_hour:02d}:{test_minute:02d} on day {datetime.now().day}")
        
        from app.celery_tasks import update_celery_schedule
        update_celery_schedule()
        
        print("🔄 Celery schedule updated!")
        print("⏰ Tasks will execute automatically in ~2 minutes")
        return test_hour, test_minute

def restore_original_schedule():
    """Restore the original 3:50 AM schedule"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Restoring original 3:50 AM schedule...")
        
        daily = AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first()
        if daily:
            daily.reminder_time = time(3, 50)
        
        monthly = AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first()
        if monthly:
            monthly.reminder_time = time(3, 50)
            monthly.report_day_of_month = 29
        
        from app.extensions import db
        db.session.commit()
        
        from app.celery_tasks import update_celery_schedule
        update_celery_schedule()
        
        print("✅ Original schedule restored:")
        print("   Daily reminders: 03:50 AM")
        print("   Monthly reports: 03:50 AM on day 29")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_original_schedule()
    else:
        print("🧪 CELERY SCHEDULE TESTING")
        print("=" * 40)
        
        test_hour, test_minute = set_test_schedule()
        
        print(f"\n🔍 Now run: python monitor_celery_tasks.py")
        print(f"⏰ Watch for execution at {test_hour:02d}:{test_minute:02d}")
        print("\n💡 To restore original schedule, run:")
        print("   python schedule_test.py restore")
