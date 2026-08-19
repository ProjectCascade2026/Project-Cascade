#!/usr/bin/env python3
"""
Import and analyze ALL Gmail messages from all folders
Cascade signal extraction from any email content
Tracks analyzed messages to avoid duplicates

Frequency: Daily 08:00 AM
"""

import imaplib
import email
from email.header import decode_header
from cascade_db import add_signal, add_finding, is_message_analyzed, mark_message_analyzed
from datetime import datetime
import configparser
import os
import re

def fetch_all_gmail_messages(gmail_user, app_password):
    """
    Fetch unanalyzed messages from ALL Gmail folders
    Returns list of messages with metadata
    """
    print("\n[IMAP] Connecting to Gmail IMAP...")

    messages_data = []

    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_user, app_password)
        print(f"[OK] Authenticated as {gmail_user}")

        # Get all folders
        status, mailbox_list = mail.list()
        print(f"\n[FOLDERS] Scanning all folders for unanalyzed messages...")

        folders_scanned = 0

        for mailbox_str in mailbox_list:
            mailbox_str = mailbox_str.decode('utf-8') if isinstance(mailbox_str, bytes) else mailbox_str

            # Extract folder name
            if '"' in mailbox_str:
                folder_name = mailbox_str.split('"')[-2]
            else:
                folder_name = mailbox_str.split()[-1]

            try:
                # Select folder
                mail.select(folder_name, readonly=True)
                folders_scanned += 1

                # Fetch all messages in folder
                status, messages = mail.search(None, 'ALL')
                email_ids = messages[0].split()

                for email_id in email_ids[-50:]:  # Last 50 messages per folder
                    status, msg_data = mail.fetch(email_id, '(RFC822)')

                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            try:
                                msg = email.message_from_bytes(response_part[1])

                                # Extract message ID
                                msg_id = msg.get('Message-ID', f"{folder_name}_{email_id.decode()}").strip('<>')

                                # Skip if already analyzed
                                if is_message_analyzed(msg_id):
                                    continue

                                # Extract headers
                                subject = msg.get('Subject', 'Untitled')
                                from_addr = msg.get('From', 'Unknown')
                                date_str = msg.get('Date', '')

                                # Parse sender name
                                author = from_addr.split('<')[0].strip() if '<' in from_addr else from_addr

                                # Extract body
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

                                messages_data.append({
                                    'message_id': msg_id,
                                    'folder': folder_name,
                                    'author': author,
                                    'subject': subject,
                                    'body': body,
                                    'date': date_formatted
                                })
                            except Exception as e:
                                continue
            except Exception as e:
                continue

        mail.close()
        mail.logout()

        print(f"[OK] Scanned {folders_scanned} folders")
        print(f"[OK] Found {len(messages_data)} unanalyzed messages")
        return messages_data

    except imaplib.IMAP4.error as e:
        print(f"[ERROR] IMAP error: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return []

def load_config():
    """Load Gmail credentials from config.ini"""
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

def extract_cascade_signals(subject, body, author, folder):
    """
    Extract cascade-relevant signals from email content
    """
    signals = []
    findings = []

    # Combine content for analysis
    content = f"{subject} {body}".lower()

    # Cascade keyword detection
    keywords = {
        'grid': (2, 'Energy System', 'Power grid incident or energy supply discussion'),
        'water': (3, 'Water System', 'Water supply or water system incident'),
        'food': (5, 'Food System', 'Food supply, agriculture, or food security discussion'),
        'supply chain': (7, 'Economic/Supply Chain', 'Supply chain disruption or logistics issue'),
        'semiconductor': (6, 'Measurement/Supply Chain', 'Semiconductor shortage or manufacturing issue'),
        'port': (7, 'Economic/Supply Chain', 'Port congestion or shipping disruption'),
        'energy': (2, 'Energy System', 'Energy supply or fuel issue'),
        'inflation': (8, 'Feedback Amplification', 'Price inflation or economic feedback loop'),
        'climate': (1, 'Climate System', 'Climate event or environmental indicator'),
        'weather': (1, 'Climate System', 'Extreme weather or meteorological event'),
        'geopolitical': (10, 'Geopolitical Risk', 'Geopolitical tension or international conflict'),
        'sanction': (10, 'Geopolitical Risk', 'Economic sanctions or trade restrictions'),
    }

    for keyword, (node_id, domain, desc) in keywords.items():
        if keyword in content:
            signal = {
                'node': node_id,
                'domain': domain,
                'description': f"{desc} - from {author}",
                'severity': 'warning',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': f"Gmail: {folder} - {subject[:50]}"
            }
            signals.append(signal)
            break  # One signal per message

    # Extract finding if significant content detected
    if signals and len(body) > 100:
        # Look for cascade-related language
        if any(word in content for word in ['cascade', 'amplify', 'fail', 'collapse', 'system']):
            finding = {
                'mechanism': 'Cascading System Failure',
                'text': f"Analysis of cascade-relevant research: {subject}. From {author} in {folder}. Key excerpt: {body[:200]}...",
                'confidence': 0.75,
                'evidence': f"Email analysis - {author}"
            }
            findings.append(finding)

    return signals, findings

def main():
    print("\n" + "="*60)
    print("[EMAIL] Analyzing All Gmail Messages")
    print("="*60 + "\n")

    # Load credentials
    gmail_user, app_password = load_config()

    if not gmail_user:
        print("   Cannot proceed without config.ini")
        return

    # Fetch unanalyzed messages
    messages_data = fetch_all_gmail_messages(gmail_user, app_password)

    if not messages_data:
        print("\n[OK] No new unanalyzed messages")
        return

    print(f"\n[PROCESSING] Processing {len(messages_data)} messages...\n")

    signal_count = 0
    finding_count = 0

    for msg in messages_data:
        try:
            # Extract signals and findings
            signals, findings = extract_cascade_signals(msg['subject'], msg['body'], msg['author'], msg['folder'])

            # Add to database
            for signal in signals:
                try:
                    add_signal(signal['node'], signal['domain'], signal['description'],
                              signal['severity'], signal['date'], signal['source'])
                    print(f"   [OK] Signal from {msg['author']}: {signal['domain']}")
                    signal_count += 1
                except Exception as e:
                    print(f"   [WARNING] Error adding signal: {e}")

            for finding in findings:
                try:
                    add_finding(finding['mechanism'], finding['text'],
                               finding['confidence'], finding['evidence'])
                    print(f"   [OK] Finding: {finding['mechanism']}")
                    finding_count += 1
                except Exception as e:
                    print(f"   [WARNING] Error adding finding: {e}")

            # Mark as analyzed
            mark_message_analyzed(msg['message_id'], msg['folder'], msg['author'],
                                 msg['subject'], msg['date'], len(signals), len(findings))

        except Exception as e:
            print(f"   [WARNING] Error processing message from {msg['author']}: {e}")
            continue

    print(f"\n[OK] Gmail Analysis Complete!")
    print(f"   - Signals added: {signal_count}")
    print(f"   - Findings added: {finding_count}")
    print(f"   - Messages analyzed: {len(messages_data)}")

if __name__ == '__main__':
    main()
