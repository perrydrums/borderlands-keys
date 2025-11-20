#!/usr/bin/env python3
"""
Borderlands 4 Shift Codes Scraper
Scrapes shift codes from MentalMars and sends email notifications for new codes.
"""

import os
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Set
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip .env loading


# Configuration
URL = "https://mentalmars.com/game-news/borderlands-4-shift-codes/"
STATE_FILE = "known_codes.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def load_known_codes() -> Set[str]:
    """Load previously seen codes from state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('codes', []))
        except (json.JSONDecodeError, KeyError):
            return set()
    return set()


def save_known_codes(codes: Set[str]):
    """Save known codes to state file."""
    data = {
        'codes': list(codes),
        'last_updated': datetime.now().isoformat()
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def extract_shift_codes(html: str) -> List[Dict[str, str]]:
    """
    Extract shift codes from the HTML page.
    Returns a list of dictionaries with code, reward, added_date, and expire_date.
    """
    soup = BeautifulSoup(html, 'html.parser')
    codes = []

    # Find the main table for "Every Borderlands 4 SHiFT Code for Golden Keys"
    # Look for the heading first, then find the table after it
    heading = soup.find('h2', string=re.compile('Every Borderlands 4 SHiFT Code for Golden Keys', re.I))

    if not heading:
        print("Warning: Could not find the main shift codes table heading")
        return codes

    # Find the table after the heading
    table = heading.find_next('figure')
    if table:
        table = table.find('table')

    if not table:
        print("Warning: Could not find the shift codes table")
        return codes

    # Extract rows (skip header row)
    rows = table.find_all('tr')[1:]  # Skip header

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:
            reward = cells[0].get_text(strip=True)
            added_date = cells[1].get_text(strip=True)

            # Extract code from the code tag
            code_elem = cells[2].find('code')
            if code_elem:
                code = code_elem.get_text(strip=True)
                # Validate code format (should be like: XXXX-XXXX-XXXX-XXXX-XXXX)
                if re.match(r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$', code):
                    expire_date = cells[3].get_text(strip=True)
                    codes.append({
                        'code': code,
                        'reward': reward,
                        'added_date': added_date,
                        'expire_date': expire_date
                    })

    return codes


def send_email_notification(new_codes: List[Dict[str, str]], recipient_email: str):
    """
    Send email notification with new shift codes.
    Uses SendGrid API if SENDGRID_API_KEY is set, otherwise uses SMTP.
    """
    if not new_codes:
        return

    # Get email configuration from environment variables
    email_provider = os.getenv('EMAIL_PROVIDER', 'smtp').lower()

    if email_provider == 'sendgrid':
        send_via_sendgrid(new_codes, recipient_email)
    elif email_provider == 'resend':
        send_via_resend(new_codes, recipient_email)
    else:
        send_via_smtp(new_codes, recipient_email)


def send_via_sendgrid(new_codes: List[Dict[str, str]], recipient_email: str):
    """Send email using SendGrid API."""
    import sendgrid
    from sendgrid.helpers.mail import Mail

    api_key = os.getenv('SENDGRID_API_KEY')
    if not api_key:
        print("Error: SENDGRID_API_KEY not set")
        return

    sg = sendgrid.SendGridAPIClient(api_key=api_key)

    subject = f"🎮 New Borderlands 4 Shift Codes Available! ({len(new_codes)} new)"
    body = format_email_body(new_codes)

    message = Mail(
        from_email=os.getenv('SENDGRID_FROM_EMAIL', recipient_email),
        to_emails=recipient_email,
        subject=subject,
        html_content=body
    )

    try:
        response = sg.send(message)
        print(f"Email sent successfully via SendGrid. Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending email via SendGrid: {e}")


def send_via_resend(new_codes: List[Dict[str, str]], recipient_email: str):
    """Send email using Resend API."""
    import resend

    api_key = os.getenv('RESEND_API_KEY')
    if not api_key:
        print("Error: RESEND_API_KEY not set")
        return

    resend.api_key = api_key

    subject = f"🎮 New Borderlands 4 Shift Codes Available! ({len(new_codes)} new)"
    body = format_email_body(new_codes)

    try:
        params = {
            "from": os.getenv('RESEND_FROM_EMAIL', 'notifications@resend.dev'),
            "to": recipient_email,
            "subject": subject,
            "html": body
        }

        email = resend.Emails.send(params)
        print(f"Email sent successfully via Resend. ID: {email.get('id')}")
    except Exception as e:
        print(f"Error sending email via Resend: {e}")


def send_via_smtp(new_codes: List[Dict[str, str]], recipient_email: str):
    """Send email using SMTP (Gmail or other SMTP server)."""
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not smtp_user or not smtp_password:
        print("Error: SMTP_USER and SMTP_PASSWORD must be set for SMTP email")
        return

    subject = f"🎮 New Borderlands 4 Shift Codes Available! ({len(new_codes)} new)"
    body = format_email_body(new_codes)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = recipient_email

    html_part = MIMEText(body, 'html')
    msg.attach(html_part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Email sent successfully via SMTP to {recipient_email}")
    except Exception as e:
        print(f"Error sending email via SMTP: {e}")


def format_email_body(new_codes: List[Dict[str, str]]) -> str:
    """Format the email body as HTML."""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .code {{
                font-family: monospace;
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }}
            .code-block {{
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
            }}
            h2 {{ color: #333; }}
            .reward {{ font-weight: bold; color: #0066cc; }}
            .date {{ color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h2>🎮 New Borderlands 4 Shift Codes!</h2>
        <p>Found <strong>{len(new_codes)}</strong> new shift code(s):</p>
    """

    for code_info in new_codes:
        html += f"""
        <div class="code-block">
            <div class="reward">{code_info['reward']}</div>
            <div class="code">{code_info['code']}</div>
            <div class="date">
                Added: {code_info['added_date']} |
                Expires: {code_info['expire_date']}
            </div>
        </div>
        """

    html += """
        <p><a href="https://shift.gearboxsoftware.com/rewards">Redeem codes on the Official SHiFT Website</a></p>
        <p><small>Source: <a href="https://mentalmars.com/game-news/borderlands-4-shift-codes/">MentalMars</a></small></p>
    </body>
    </html>
    """

    return html


def main():
    """Main function to scrape codes and send notifications."""
    print(f"Starting scrape at {datetime.now()}")

    # Get recipient email from environment
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    if not recipient_email:
        print("Warning: RECIPIENT_EMAIL not set. Email notifications will be skipped.")

    # Load known codes
    known_codes = load_known_codes()
    print(f"Loaded {len(known_codes)} known codes")

    # Fetch the page
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return

    # Extract codes
    codes = extract_shift_codes(response.text)
    print(f"Found {len(codes)} codes on the page")

    # Find new codes
    new_codes = [code for code in codes if code['code'] not in known_codes]

    if new_codes:
        print(f"Found {len(new_codes)} new code(s):")
        for code_info in new_codes:
            print(f"  - {code_info['code']} ({code_info['reward']})")

        # Update known codes
        for code_info in new_codes:
            known_codes.add(code_info['code'])
        save_known_codes(known_codes)

        # Send email notification
        if recipient_email:
            send_email_notification(new_codes, recipient_email)
        else:
            print("Skipping email notification (RECIPIENT_EMAIL not set)")
    else:
        print("No new codes found")

    print(f"Scrape completed at {datetime.now()}")


if __name__ == "__main__":
    main()
