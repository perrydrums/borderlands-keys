#!/usr/bin/env python3
"""
Test script to verify email functionality with improved formatting.
"""

import os
from scraper import send_email_notification, format_email_body, format_email_body_plain

# Set test recipient (use your actual email from .env)
recipient_email = os.getenv('RECIPIENT_EMAIL', 'test@example.com')

# Create mock new codes
test_codes = [
    {
        'code': 'TEST1-2TEST-3TEST-4TEST-5TEST',
        'reward': '3 Golden Key',
        'added_date': 'Nov 20, 2025',
        'expire_date': 'Nov 27, 2025'
    }
]

print("Testing email formatting...")
print("\n" + "="*50)
print("HTML Version:")
print("="*50)
html = format_email_body(test_codes)
print(html[:500] + "...")

print("\n" + "="*50)
print("Plain Text Version:")
print("="*50)
plain = format_email_body_plain(test_codes)
print(plain)

print("\n" + "="*50)
print("Sending test email...")
print("="*50)

if recipient_email == 'test@example.com':
    print("Warning: RECIPIENT_EMAIL not set. Set it in .env or as environment variable.")
    print("Skipping actual email send.")
else:
    try:
        send_email_notification(test_codes, recipient_email)
        print(f"\n✅ Test email sent successfully to {recipient_email}!")
        print("Check your inbox (and spam folder) to verify the improved formatting.")
    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
