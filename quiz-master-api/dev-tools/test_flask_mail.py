#!/usr/bin/env python3
"""
Test Flask-Mail configuration for daily reminders
"""
import os
import sys
sys.path.append('.')

from app import create_app
from app.extensions import mail
from flask_mail import Message

def test_flask_mail():
    print("=== Testing Flask-Mail Configuration ===")
    
    app = create_app()
    
    with app.app_context():
        print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"MAIL_PASSWORD: {'SET' if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            print("\n❌ ERROR: Flask-Mail credentials not configured!")
            return False
        
        try:
            test_email = app.config.get('MAIL_USERNAME')
            
            msg = Message(
                subject="Distributed Assessment Platform - Flask-Mail Test",
                sender=("Distributed Assessment Platform", "noreply@assessmentplatform.com"),
                recipients=[test_email],
                body="This is a test email to verify Flask-Mail functionality for daily reminders."
            )
            
            msg.html = """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #4285f4;">📚 Distributed Assessment Platform - Flask-Mail Test</h2>
                <p>This is a test email to verify Flask-Mail functionality for daily reminders.</p>
                <p>If you received this email, Flask-Mail is working correctly!</p>
            </div>
            """
            
            print(f"\n📧 Attempting to send Flask-Mail test email to: {test_email}")
            
            mail.send(msg)
            
            print("✅ SUCCESS: Flask-Mail test email sent successfully!")
            print("Check your inbox for the Flask-Mail test email.")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Flask-Mail failed: {str(e)}")
            return False

if __name__ == "__main__":
    test_flask_mail()
