#!/usr/bin/env python3
"""
Import Substack emails via Gmail IMAP (no Google Cloud Console needed)
Simple email fetching using standard IMAP protocol
"""

import imaplib
import email
from email.header import decode_header
from cascade_db import add_signal, add_finding
from datetime import datetime
import configparser
import os

def fetch_substack_emails_imap(gmail_user, app_password, folder="Substack", max_emails=20):
    """
    Fetch Substack emails from Gmail using IMAP.

    Args:
        gmail_user: Your Gmail address (e.g., michael@strangelove.com)
        app_password: App-specific password (16-character code from Google Account)
        folder: Gmail label/folder name (default: "Substack")
        max_emails: Maximum emails to fetch

    Returns:
        List of email dicts with author, subject, body, date
    """

    print(f"[IMAP] Connecting to Gmail IMAP...")

    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_user, app_password)
        print(f"[OK] Authenticated as {gmail_user}")

        # List available folders
        status, mailbox_list = mail.list()

        # Find Substack folder
        substack_folder_name = None
        print(f"\n[FOLDERS] Available folders:")
        for mailbox_str in mailbox_list:
            mailbox_str = mailbox_str.decode('utf-8') if isinstance(mailbox_str, bytes) else mailbox_str
            if 'Substack' in mailbox_str or 'substack' in mailbox_str:
                # Extract folder name
                if '"' in mailbox_str:
                    substack_folder_name = mailbox_str.split('"')[-2]
                else:
                    substack_folder_name = mailbox_str.split()[-1]
                print(f"   [+] Found: {substack_folder_name}")
                break
            elif folder.lower() in mailbox_str.lower():
                if '"' in mailbox_str:
                    substack_folder_name = mailbox_str.split('"')[-2]
                else:
                    substack_folder_name = mailbox_str.split()[-1]
                print(f"   [+] Found: {substack_folder_name}")
                break

        if not substack_folder_name:
            print(f"\n[ERROR] Folder '{folder}' not found")
            print(f"   First 10 available folders:")
            for i, mailbox_str in enumerate(mailbox_list[:10]):
                mailbox_str = mailbox_str.decode('utf-8') if isinstance(mailbox_str, bytes) else mailbox_str
                print(f"      {i+1}. {mailbox_str}")
            mail.close()
            return []

        # Select folder
        try:
            mail.select(substack_folder_name, readonly=True)
            print(f"[OK] Opened folder: {substack_folder_name}\n")
        except Exception as e:
            print(f"[ERROR] Could not open folder: {e}")
            # Try with quotes if folder name has spaces
            try:
                mail.select(f'"{substack_folder_name}"', readonly=True)
                print(f"[OK] Opened folder: {substack_folder_name}\n")
            except:
                mail.close()
                return []

        # Fetch recent emails
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()

        # Get last N emails (most recent first)
        email_ids = email_ids[-max_emails:][::-1]

        emails_data = []

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Extract headers
                    subject = msg.get('Subject', 'Untitled')
                    from_addr = msg.get('From', 'Unknown')
                    date_str = msg.get('Date', '')

                    # Parse sender name
                    author = from_addr.split('<')[0].strip() if '<' in from_addr else from_addr

                    # Extract body (prefer plain text)
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body = msg.get_payload()

                    # Format date
                    try:
                        from email.utils import parsedate_to_datetime
                        dt = parsedate_to_datetime(date_str)
                        date_formatted = dt.strftime('%Y-%m-%d')
                    except:
                        date_formatted = datetime.now().strftime('%Y-%m-%d')

                    emails_data.append({
                        'author': author,
                        'subject': subject,
                        'body': body,
                        'date': date_formatted
                    })

        mail.close()
        mail.logout()

        print(f"[OK] Fetched {len(emails_data)} emails from {folder}")
        return emails_data

    except imaplib.IMAP4.error as e:
        print(f"[ERROR] IMAP error: {e}")
        print("   Make sure:")
        print("   1. You enabled 2-factor authentication on your Google Account")
        print("   2. You created an app-specific password (16-character code)")
        print("   3. You're using the correct app password, not your Google password")
        return []
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return []

def load_config():
    """Load Gmail credentials from config.ini"""
    import configparser
    config = configparser.ConfigParser()

    if not os.path.exists('config.ini'):
        print("[ERROR] config.ini not found")
        print("   Create config.ini with:")
        print("   [gmail]")
        print("   email = your.email@gmail.com")
        print("   app_password = your16charpassword")
        return None, None

    config.read('config.ini')
    try:
        gmail_user = config.get('gmail', 'email')
        app_password = config.get('gmail', 'app_password')
        return gmail_user, app_password
    except:
        print("[ERROR] Invalid config.ini format")
        return None, None

def main():
    print("\n" + "="*60)
    print("[EMAIL] Importing Substack Emails via Gmail IMAP")
    print("="*60 + "\n")

    # Load credentials from config file (for automation)
    gmail_user, app_password = load_config()

    if not gmail_user:
        print("   Cannot proceed without config.ini")
        return

    # Fetch emails
    emails_data = fetch_substack_emails_imap(gmail_user, app_password)

    if not emails_data:
        print("\n[WARNING] No emails fetched")
        return

    # Import them
    from import_substack_signals import import_substack_signals

    print(f"\n[PROCESSING] Processing {len(emails_data)} emails...\n")
    signal_count, finding_count = import_substack_signals(emails_data)

    print(f"\n[OK] Import Complete!")
    print(f"   • Signals added: {signal_count}")
    print(f"   • Findings added: {finding_count}")
    print(f"   • Total entries: {signal_count + finding_count}")
    print("\n" + "="*60)
    print("\n🎯 Next: Check your dashboard at")
    print("   https://project-cascade-strangelove.streamlit.app/")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
