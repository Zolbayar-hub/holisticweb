#!/usr/bin/env python3
"""
Simple email test script to verify email functionality works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_app import app, mail
from flask_mail import Message

def test_email():
    """Test sending email directly"""
    with app.app_context():
        try:
            print("🧪 Testing email functionality...")
            print(f"📧 SMTP Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            print(f"📧 Username: {app.config['MAIL_USERNAME']}")
            print(f"📧 From: {app.config['MAIL_DEFAULT_SENDER']}")
            
            # Create test message
            msg = Message(
                subject="🧪 Test Email from HolisticWeb",
                recipients=["dambazolbayar@gmail.com"],  # Send to admin
                sender=app.config['MAIL_DEFAULT_SENDER'],
                body="""This is a test email to verify the email functionality is working.

If you receive this email, the email configuration is correct!

Sent from: HolisticWeb Test Script
Time: Test time
"""
            )
            
            print("📧 Sending test email...")
            mail.send(msg)
            print("✅ Test email sent successfully!")
            
        except Exception as e:
            print(f"❌ Email test failed: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=== Email Test ===")
    test_email()
    print("Done!")
