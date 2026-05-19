#!/usr/bin/env python3
"""
Demo script to test monthly reports functionality
"""

import os
import sys
sys.path.append(os.path.abspath('.'))

from app import create_app
from app.common.report_service import ReportService
from app.models.user import User
from app.models.notification import AdminNotificationSetting
from datetime import datetime

def demo_monthly_reports():
    """Demo the monthly reports functionality"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Distributed Assessment Platform - Monthly Reports Demo")
        print("=" * 50)
        
        monthly_setting = AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first()
        if monthly_setting:
            print(f"✅ Monthly reports configured for {monthly_setting.reminder_time} on day {monthly_setting.report_day_of_month}")
        else:
            print("❌ Monthly reports not configured")
            return
        
        users = User.query.filter_by(status='active').filter(User.role != 'admin').limit(3).all()
        
        if not users:
            print("❌ No active users found")
            return
        
        print(f"\n📊 Generating monthly reports for {len(users)} users...")
        
        for user in users:
            print(f"\n👤 Processing user: {user.fullname} ({user.email})")
            
            now = datetime.now()
            report_month = now.month
            report_year = now.year
            
            try:
                report_data = ReportService._generate_monthly_report_data(user, report_year, report_month)
                
                if report_data['has_activity']:
                    print(f"   ✅ Activity found: {report_data['total_quizzes']} quizzes, {report_data['average_score']:.1f}% avg")
                    print(f"   📈 Ranking: #{report_data['user_rank']} out of {report_data['total_participants']}")
                    print(f"   🏆 Best quiz: {report_data['best_quiz']['quiz_name']} ({report_data['best_quiz']['percentage']:.1f}%)")
                    
                    print(f"   📧 Monthly report would be sent to {user.email}")
                else:
                    print(f"   ⚠️  No activity found for this month")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print(f"\n🎯 Demo completed! Use the following to trigger actual reports:")
        print(f"   POST /api/admin/report/trigger-monthly-reports")
        
        print(f"\n📋 Testing CSV export...")
        if users:
            sample_user = users[0]
            csv_result = ReportService.export_user_csv(sample_user.id)
            print(f"   CSV Export result: {csv_result}")

if __name__ == "__main__":
    demo_monthly_reports()
