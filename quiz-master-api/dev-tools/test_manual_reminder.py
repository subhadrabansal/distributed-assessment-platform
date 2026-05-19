#!/usr/bin/env python3
"""Manually trigger daily reminder for testing"""
from app import create_app
from app.common.reminder_service import ReminderService

def test_manual_reminder():
    print("=== Manual Daily Reminder Test ===")
    app = create_app()
    with app.app_context():
        print("🔄 Triggering daily reminders manually...")
        try:
            result = ReminderService.send_daily_reminders_at_time(22, 25)
            print(f"✅ Result: {result}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_manual_reminder()
