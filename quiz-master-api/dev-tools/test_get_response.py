#!/usr/bin/env python3
"""Simple test to check GET response structure"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.notification import AdminNotificationSetting
import json

def test_get_response():
    app = create_app()
    
    with app.app_context():
        daily = AdminNotificationSetting.query.filter_by(setting_type='daily_reminder').first()
        monthly = AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first()
        
        result = {}
        
        if daily:
            result['daily_reminder'] = {
                'reminder_time': daily.reminder_time.strftime('%H:%M') if daily.reminder_time else '08:00',
                'reminder_channel': daily.reminder_channel or 'email'
            }
        
        if monthly:
            result['monthly_report'] = {
                'reminder_time': monthly.reminder_time.strftime('%H:%M') if monthly.reminder_time else '08:00',
                'report_day_of_month': monthly.report_day_of_month or 1,
                'report_format': monthly.report_format or 'html',
                'report_channel': monthly.report_channel or 'email'
            }
        
        print("Expected GET response data:")
        print(json.dumps(result, indent=2))
        
        print(f"\nDirect field values:")
        print(f"monthly.report_format = '{monthly.report_format}' (type: {type(monthly.report_format)})")
        print(f"monthly.report_format or 'html' = '{monthly.report_format or 'html'}'")

if __name__ == '__main__':
    test_get_response()
