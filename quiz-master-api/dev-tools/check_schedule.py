#!/usr/bin/env python3
"""Check current Celery Beat schedule"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.celery_app import celery

def check_celery_schedule():
    print("=== Current Celery Beat Schedule ===")
    app = create_app()
    with app.app_context():
        schedule = celery.conf.beat_schedule
        if schedule:
            for task_name, task_config in schedule.items():
                print(f"\n📅 Task: {task_name}")
                print(f"   Function: {task_config['task']}")
                print(f"   Schedule: {task_config['schedule']}")
                if 'args' in task_config:
                    print(f"   Args: {task_config['args']}")
        else:
            print("❌ No scheduled tasks found!")

if __name__ == "__main__":
    check_celery_schedule()
