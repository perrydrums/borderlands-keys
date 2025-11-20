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
    Send email notification with new shift codes using Mailjet.
    """
    if not new_codes:
        return

    send_via_mailjet(new_codes, recipient_email)


def send_via_mailjet(new_codes: List[Dict[str, str]], recipient_email: str):
    """Send email using Mailjet API."""
    from mailjet_rest import Client

    api_key = os.getenv('MAILJET_API_KEY')
    api_secret = os.getenv('MAILJET_API_SECRET')

    if not api_key or not api_secret:
        print("Error: MAILJET_API_KEY and MAILJET_API_SECRET must be set")
        return

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    # Less spammy subject line (removed emoji)
    subject = f"New Borderlands 4 Shift Codes Available ({len(new_codes)} new)"

    html_body = format_email_body(new_codes)
    plain_text_body = format_email_body_plain(new_codes)

    from_email = os.getenv('MAILJET_FROM_EMAIL', recipient_email)
    from_name = os.getenv('MAILJET_FROM_NAME', 'Borderlands Monitor')

    data = {
        'Messages': [
            {
                'From': {
                    'Email': from_email,
                    'Name': from_name
                },
                'To': [
                    {
                        'Email': recipient_email
                    }
                ],
                'Subject': subject,
                'TextPart': plain_text_body,
                'HTMLPart': html_body,
                'ReplyTo': {
                    'Email': from_email,
                    'Name': from_name
                }
            }
        ]
    }

    try:
        result = mailjet.send.create(data=data)
        status_code = result.status_code
        if status_code == 200:
            print(f"Email sent successfully via Mailjet. Status: {status_code}")
        else:
            print(f"Email sent via Mailjet with status: {status_code}")
            print(f"Response: {result.json()}")
    except Exception as e:
        print(f"Error sending email via Mailjet: {e}")


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


def format_email_body_plain(new_codes: List[Dict[str, str]]) -> str:
    """Format the email body as plain text."""
    text = f"New Borderlands 4 Shift Codes Available!\n\n"
    text += f"Found {len(new_codes)} new shift code(s):\n\n"

    for code_info in new_codes:
        text += f"{code_info['reward']}\n"
        text += f"Code: {code_info['code']}\n"
        text += f"Added: {code_info['added_date']} | Expires: {code_info['expire_date']}\n\n"

    text += "Redeem codes on the Official SHiFT Website:\n"
    text += "https://shift.gearboxsoftware.com/rewards\n\n"
    text += "Source: https://mentalmars.com/game-news/borderlands-4-shift-codes/\n"

    return text


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
