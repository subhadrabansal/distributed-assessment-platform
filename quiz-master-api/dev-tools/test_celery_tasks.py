#!/usr/bin/env python3
"""
Test script for Celery tasks - Manual trigger for testing
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.celery_tasks import send_daily_reminders_at_time, send_monthly_reports

def test_daily_reminders():
    """Test daily reminders task"""
    print("🔔 Testing Daily Reminders Task...")
    try:
        result = send_daily_reminders_at_time.delay(3, 50)
        print(f"✅ Daily reminders task queued with ID: {result.id}")
        
        try:
            task_result = result.get(timeout=30)
            print(f"📧 Task completed: {task_result}")
        except Exception as e:
            print(f"⏰ Task is running in background: {e}")
            
    except Exception as e:
        print(f"❌ Error triggering daily reminders: {e}")

def test_monthly_reports():
    """Test monthly reports task"""
    print("\n📊 Testing Monthly Reports Task...")
    try:
        result = send_monthly_reports.delay()
        print(f"✅ Monthly reports task queued with ID: {result.id}")
        
        try:
            task_result = result.get(timeout=60)
            print(f"📋 Task completed: {task_result}")
        except Exception as e:
            print(f"⏰ Task is running in background: {e}")
            
    except Exception as e:
        print(f"❌ Error triggering monthly reports: {e}")

def check_task_status(task_id):
    """Check the status of a specific task"""
    from app.celery_app import celery
    result = celery.AsyncResult(task_id)
    print(f"Task {task_id}: {result.status}")
    if result.ready():
        print(f"Result: {result.result}")

def main():
    app = create_app()
    with app.app_context():
        print("🚀 Testing Celery Tasks for 3:50 AM Schedule")
        print("=" * 50)
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "daily":
                test_daily_reminders()
            elif sys.argv[1] == "monthly":
                test_monthly_reports()
            elif sys.argv[1] == "status" and len(sys.argv) > 2:
                check_task_status(sys.argv[2])
            else:
                print("Usage: python test_celery_tasks.py [daily|monthly|status <task_id>]")
        else:
            # Test both
            test_daily_reminders()
            test_monthly_reports()
            
        print("\n🔍 You can check the logs in the Celery worker terminal to see the actual execution.")
        print("📋 Check the admin dashboard for reminder logs and report history.")

if __name__ == "__main__":
    main()
