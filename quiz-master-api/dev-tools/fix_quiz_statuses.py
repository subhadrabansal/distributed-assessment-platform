#!/usr/bin/env python3
"""
Fix quiz statuses based on current date/time
Update quizzes that should have status changes
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.quiz import Quiz
from app.extensions import db
from datetime import datetime

def update_quiz_statuses():
    """Update quiz statuses based on current date/time"""
    app = create_app()
    
    with app.app_context():
        from app.common.quiz_status_manager import QuizStatusManager
        
        print("🔄 Checking and updating quiz statuses...")
        print("=" * 50)
        
        result = QuizStatusManager.update_all_quiz_statuses(context='manual_dev_tool')
        
        print(f"📊 Status Update Summary:")
        print(f"   Total quizzes: {result['total_quizzes']}")
        print(f"   Updated: {result['updated_count']}")
        print()
        
        if result['updates']:
            print("📋 Detailed Updates:")
            for update in result['updates']:
                print(f"Quiz {update['quiz_id']}: {update['quiz_name']}")
                print(f"  Status: {update['old_status']} → {update['new_status']}")
                print(f"  Start: {update['start_date']}")
                print(f"  End: {update['end_date']}")
                print()
        
        if result['errors']:
            print("❌ Errors encountered:")
            for error in result['errors']:
                print(f"  Quiz {error.get('quiz_id', 'unknown')}: {error['error']}")
            print()
        
        if result['updated_count'] > 0:
            print(f"🎉 Successfully updated {result['updated_count']} quiz statuses!")
        else:
            print("✅ All quiz statuses are already correct!")
        
        summary = QuizStatusManager.get_quiz_status_summary()
        print(f"\n📊 Current Status Distribution:")
        print(f"   Upcoming: {summary['upcoming']}")
        print(f"   Ongoing: {summary['ongoing']}")
        print(f"   Completed: {summary['completed']}")
        print(f"   Cancelled: {summary['cancelled']}")
        
        if summary['status_mismatches']:
            print(f"\n⚠️  Status Mismatches Found: {len(summary['status_mismatches'])}")
            for mismatch in summary['status_mismatches']:
                print(f"   Quiz {mismatch['quiz_id']}: {mismatch['current_status']} should be {mismatch['expected_status']}")
        
        if summary['upcoming_transitions']:
            print(f"\n⏰ Starting Soon (next 24h): {len(summary['upcoming_transitions'])}")
            for transition in summary['upcoming_transitions']:
                print(f"   Quiz {transition['quiz_id']}: starts in {transition['starts_in_hours']} hours")
        
        if summary['ending_soon']:
            print(f"\n⏳ Ending Soon (next 24h): {len(summary['ending_soon'])}")
            for ending in summary['ending_soon']:
                print(f"   Quiz {ending['quiz_id']}: ends in {ending['ends_in_hours']} hours")

if __name__ == "__main__":
    update_quiz_statuses()
