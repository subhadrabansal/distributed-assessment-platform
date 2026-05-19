#!/usr/bin/env python3
"""
Monitor Celery task execution in real-time
Watch for scheduled tasks at 3:50 AM
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime, timedelta
from app import create_app
from app.models.notification import ReminderLog, ReportHistory

def monitor_tasks():
    """Monitor for new task executions"""
    app = create_app()
    
    print("🔍 Monitoring Celery Tasks - Waiting for 3:50 AM execution...")
    print("=" * 60)
    
    # Get baseline counts
    with app.app_context():
        initial_reminder_count = ReminderLog.query.count()
        initial_report_count = ReportHistory.query.count()
        
    print(f"📊 Initial counts:")
    print(f"   Reminder logs: {initial_reminder_count}")
    print(f"   Report history: {initial_report_count}")
    print()
    
    last_check = datetime.now()
    
    while True:
        current_time = datetime.now()
        
        if (current_time - last_check).seconds >= 30:
            with app.app_context():
                recent_time = datetime.utcnow() - timedelta(minutes=2)
                
                new_reminders = ReminderLog.query.filter(
                    ReminderLog.sent_at >= recent_time
                ).order_by(ReminderLog.sent_at.desc()).all()
                
                new_reports = ReportHistory.query.filter(
                    ReportHistory.created_at >= recent_time
                ).order_by(ReportHistory.created_at.desc()).all()
                
                current_reminder_count = ReminderLog.query.count()
                current_report_count = ReportHistory.query.count()
                
                if current_reminder_count > initial_reminder_count or new_reminders:
                    print(f"🔔 NEW REMINDER ACTIVITY DETECTED!")
                    for reminder in new_reminders:
                        print(f"   {reminder.sent_at} - User {reminder.user_id} via {reminder.channel}: {reminder.status}")
                    initial_reminder_count = current_reminder_count
                    
                if current_report_count > initial_report_count or new_reports:
                    print(f"📊 NEW REPORT ACTIVITY DETECTED!")
                    for report in new_reports:
                        print(f"   {report.created_at} - User {report.user_id}: {report.report_type} ({report.status})")
                    initial_report_count = current_report_count
                
            time_str = current_time.strftime("%H:%M:%S")
            if current_time.minute == 50 and current_time.hour == 3:
                print(f"🚨 {time_str} - IT'S 3:50 AM! Tasks should be executing now!")
            elif current_time.minute in [49, 50, 51] and current_time.hour == 3:
                print(f"⏰ {time_str} - Close to 3:50 AM execution time...")
            else:
                print(f"⏰ {time_str} - Monitoring... (Next check: 3:50 AM)", end='\r')
                
            last_check = current_time
            
        time.sleep(5)  

if __name__ == "__main__":
    try:
        monitor_tasks()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
