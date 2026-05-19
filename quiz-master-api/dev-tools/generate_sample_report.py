#!/usr/bin/env python3
"""
Generate a sample monthly report HTML for demonstration
"""

import os
import sys
sys.path.append(os.path.abspath('.'))

from app import create_app
from app.common.report_service import ReportService
from app.models.user import User
from datetime import datetime

def generate_sample_report():
    """Generate a sample HTML report and save it to file"""
    
    app = create_app()
    
    with app.app_context():
        print("📊 Generating sample monthly report HTML...")
        
        user = User.query.filter_by(email='23f1000704@ds.study.iitm.ac.in').first()
        
        if not user:
            print("❌ Sample user not found")
            return
        
        now = datetime.now()
        report_data = ReportService._generate_monthly_report_data(user, now.year, now.month)
        
        if not report_data['has_activity']:
            print("❌ No activity found for sample user")
            return
        
        html_content = ReportService._create_monthly_report_html(user, report_data, now.year, now.month)
        
        filename = f"sample_monthly_report_{now.strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join('exports', filename)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Sample monthly report generated: {filepath}")
        print(f"📧 Open this file in a browser to see how the email will look!")
        
        text_content = ReportService._create_monthly_report_text(user, report_data, now.year, now.month)
        text_filename = f"sample_monthly_report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        text_filepath = os.path.join('exports', text_filename)
        
        with open(text_filepath, 'w') as f:
            f.write(text_content)
        
        print(f"📄 Text version also generated: {text_filepath}")

if __name__ == "__main__":
    generate_sample_report()
