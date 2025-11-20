#!/usr/bin/env python3
"""
Quick test script to verify the scraper works without sending emails.
"""

import os
import sys

# Set a test recipient email to prevent actual email sending
os.environ['RECIPIENT_EMAIL'] = 'test@example.com'
os.environ['EMAIL_PROVIDER'] = 'smtp'  # Will fail gracefully if SMTP not configured

# Import and run the scraper
from scraper import main

if __name__ == "__main__":
    print("Testing scraper (no emails will be sent)...")
    print("-" * 50)
    try:
        main()
        print("-" * 50)
        print("Test completed successfully!")
        print("\nNote: If you see 'Error sending email', that's expected.")
        print("Configure email settings in GitHub Secrets for production.")
    except Exception as e:
        print(f"Error during test: {e}")
        sys.exit(1)
