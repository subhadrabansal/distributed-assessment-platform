#!/usr/bin/env python3
"""Check reminder logs and user activity for testing"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.notification import ReminderLog
from app.models.user import User
from datetime import datetime, timedelta

def check_reminder_status():
    print("=== Daily Reminder System Status ===")
    app = create_app()
    with app.app_context():

        recent_logs = ReminderLog.query.filter(
            ReminderLog.sent_at >= datetime.now() - timedelta(hours=1)
        ).all()
        
        print(f"\n📧 Recent Reminders (last hour): {len(recent_logs)}")
        for log in recent_logs:
            user = User.query.get(log.user_id)
            print(f"   User: {user.fullname} ({user.email})")
            print(f"   Time: {log.sent_at}")
            print(f"   Status: {log.status}")
            print()
        

        print("\n👥 Users eligible for reminders:")
        users = User.query.filter_by(role='student').all()
        for user in users:
            last_login = user.last_login or datetime(1900, 1, 1)
            days_since_login = (datetime.now() - last_login).days
            print(f"   {user.fullname} ({user.email})")
            print(f"      Last login: {last_login}")
            print(f"      Days since login: {days_since_login}")
            print(f"      Would get reminder: {'Yes' if days_since_login >= 3 else 'No'}")
            print()

if __name__ == "__main__":
    check_reminder_status()
