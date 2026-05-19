#!/usr/bin/env python3
"""Test script to debug the settings API issue"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.notification import AdminNotificationSetting
from app.extensions import db
import json

def test_settings_api():
    app = create_app()
    
    with app.app_context():
        print("=== TESTING GET /admin/settings ===")
        from app.api.admin.admin_settings_api import get_admin_settings
        
        try:
            response = get_admin_settings()
            print("GET Response:", json.dumps(response, indent=2, default=str))
        except Exception as e:
            print("GET Error:", e)
        
        print("\n=== CURRENT DATABASE STATE ===")
        monthly = AdminNotificationSetting.query.filter_by(setting_type='monthly_report').first()
        if monthly:
            print(f"Monthly report settings:")
            print(f"  - report_format: {monthly.report_format}")
            print(f"  - report_day_of_month: {monthly.report_day_of_month}")
            print(f"  - report_channel: {monthly.report_channel}")
            print(f"  - reminder_time: {monthly.reminder_time}")
        
        print("\n=== TESTING PUT /admin/settings/monthly_report ===")
        test_data = {
            'report_format': 'pdf',
            'report_day_of_month': 15,
            'report_channel': 'email',
            'reminder_time': '10:30'
        }
        
        print(f"Sending data: {test_data}")
        
        try:
            from app.api.admin.admin_settings_api import update_admin_setting
            response = update_admin_setting('monthly_report')
            print("PUT Response:", response)
        except Exception as e:
            print("PUT Error:", e)
        
        print("\n=== DATABASE STATE AFTER UPDATE ===")
        db.session.refresh(monthly)
        if monthly:
            print(f"Monthly report settings after update:")
            print(f"  - report_format: {monthly.report_format}")
            print(f"  - report_day_of_month: {monthly.report_day_of_month}")
            print(f"  - report_channel: {monthly.report_channel}")
            print(f"  - reminder_time: {monthly.reminder_time}")

if __name__ == '__main__':
    test_settings_api()
