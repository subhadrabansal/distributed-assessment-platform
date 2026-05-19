#!/usr/bin/env python3
"""
Demo script to test the CSV export functionality
"""

import os
import sys
sys.path.append(os.path.abspath('.'))

from app import create_app
from app.common.report_service import ReportService
from app.models.user import User
from app.models.notification import ReportHistory
from app.extensions import db
from datetime import datetime
import json

def demo_csv_export():
    """Demo the CSV export functionality"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Distributed Assessment Platform - CSV Export Demo")
        print("=" * 50)
        

        user = User.query.filter_by(status='active').filter(User.role != 'admin').first()
        
        if not user:
            print("❌ No active users found")
            return
        
        print(f"👤 Testing CSV export for user: {user.fullname} ({user.email})")
        

        export_record = ReportHistory(
            user_id=user.id,
            month=datetime.now().strftime('%Y-%m'),
            report_type='csv_export',
            status='pending'
        )
        db.session.add(export_record)
        db.session.commit()
        
        print(f"📋 Created export record: {export_record.id}")

        try:
            result = ReportService.export_user_csv_enhanced(user.id, export_record.id)
            print(f"✅ Export result: {result}")
            

            if "successfully" in result:
                filename = result.split(": ")[-1]
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    print(f"📁 File created: {filename} ({file_size} bytes)")
                    

                    print("\n📊 CSV Content Preview:")
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:5] 
                        for i, line in enumerate(lines):
                            print(f"   {i+1}: {line.strip()}")
                        if len(lines) == 5:
                            print("   ... (truncated)")
                else:
                    print(f"❌ File not found: {filename}")
            
            db.session.refresh(export_record)
            print(f"📈 Export status: {export_record.status}")
            
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
        
        print(f"\n🎯 Demo completed!")
        print(f"   API Endpoints available:")
        print(f"   - POST /api/user/export/trigger-csv-export")
        print(f"   - GET /api/user/export/export-status/<export_id>")
        print(f"   - GET /api/user/export/my-exports")
        print(f"   - GET /api/user/export/download/<filename>")

if __name__ == "__main__":
    demo_csv_export()
