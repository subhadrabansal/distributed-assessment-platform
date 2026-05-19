#!/usr/bin/env python3
"""
Test script to verify OTP email sending functionality
"""
import os
import sys
sys.path.append('.')

from app.common.utils import send_email
from app.common.config import Config

def test_otp_email():
    print("=== Testing OTP Email Configuration ===")
    
    print(f"IITM_EMAIL_USER: {os.environ.get('IITM_EMAIL_USER', 'NOT SET')}")
    print(f"IITM_EMAIL_PASS: {'SET' if os.environ.get('IITM_EMAIL_PASS') else 'NOT SET'}")
    
    print(f"Config.IITM_EMAIL_USER: {Config.IITM_EMAIL_USER}")
    print(f"Config.IITM_EMAIL_PASS: {'SET' if Config.IITM_EMAIL_PASS else 'NOT SET'}")
    
    if not Config.IITM_EMAIL_USER or not Config.IITM_EMAIL_PASS:
        print("\n❌ ERROR: Email credentials not configured!")
        print("\nTo fix this, set environment variables:")
        print("export IITM_EMAIL_USER='your-email@gmail.com'")
        print("export IITM_EMAIL_PASS='your-app-password'")
        return False
    
    test_email = Config.IITM_EMAIL_USER
    subject = "Distributed Assessment Platform - Test OTP"
    body = "Test OTP: 123456\n\nThis is a test email to verify OTP functionality."
    
    print(f"\n📧 Attempting to send test email to: {test_email}")
    
    try:
        result = send_email(test_email, subject, body)
        if result:
            print("✅ SUCCESS: Test email sent successfully!")
            print("Check your inbox for the test OTP email.")
            return True
        else:
            print("❌ FAILED: Email sending failed!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_otp_email()
