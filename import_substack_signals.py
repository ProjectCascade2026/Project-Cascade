#!/usr/bin/env python3
"""
Import signals from Substack emails: Global critical infrastructure research
Extract cascade-relevant signals and research findings from Substack newsletters
Fetches emails from Gmail "Substack" folder via Gmail API
"""

from cascade_db import add_signal, add_finding
from datetime import datetime
import re
import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import email

def authenticate_gmail():
    """
    Authenticate with Gmail API.
    Uses OAuth2 flow with local credentials.json file.
    On first run, opens browser for user authorization.
    Saves token to token.pickle for subsequent runs.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None

    # Load existing token if available
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid creds, perform OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json must be downloaded from Google Cloud Console
            if not os.path.exists('credentials.json'):
                print("❌ Missing credentials.json")
                print("   Download OAuth2 credentials from Google Cloud Console:")
                print("   1. Go to https://console.cloud.google.com")
                print("   2. Create OAuth2 Desktop App credentials")
                print("   3. Download as credentials.json to this folder")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def fetch_substack_emails_from_gmail(max_results=10):
    """
    Fetch Substack emails from Gmail 'Substack' folder.

    Returns list of email dicts with:
    {
        'author': 'Email From name',
        'subject': 'Email subject line',
        'body': 'Email body content',
        'date': 'YYYY-MM-DD formatted date'
    }
    """
    creds = authenticate_gmail()
    if not creds:
        return []

    try:
        service = build('gmail', 'v1', credentials=creds)

        # Get label ID for 'Substack' folder
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        substack_label_id = None
        for label in labels:
            if label['name'].lower() == 'substack':
                substack_label_id = label['id']
                break

        if not substack_label_id:
            print("⚠ 'Substack' label not found in Gmail")
            print("   Create a Gmail label 'Substack' and label Substack emails with it")
            return []

        # Fetch messages from Substack label
        results = service.users().messages().list(
            userId='me',
            labelIds=[substack_label_id],
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        emails_data = []

        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            headers = msg['payload'].get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}

            # Extract email components
            author = header_dict.get('From', 'Unknown').split('<')[0].strip()
            subject = header_dict.get('Subject', 'Untitled')
            date_str = header_dict.get('Date', '')

            # Parse email body (handle multipart)
            body = ''
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            else:
                data = msg['payload']['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')

            # Format date to YYYY-MM-DD
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

        print(f"✅ Fetched {len(emails_data)} Substack emails from Gmail")
        return emails_data

    except Exception as e:
        print(f"❌ Error fetching Substack emails: {e}")
        return []

def parse_substack_email(email_subject, email_body, author):
    """
    Parse Substack email for cascade signals and findings.
    Extracts cascade-relevant information from newsletter content.
    Maps to cascade nodes and identifies mechanisms.
    """

    signals = []
    findings = []

    # Cascade node mapping (keyword -> node_id, mechanism, severity)
    cascade_keywords = {
        'semiconductor': (11, 'Supply Chain Fragility', 'critical'),
        'chip': (11, 'Supply Chain Fragility', 'critical'),
        'fab': (11, 'Supply Chain Fragility', 'warning'),
        'tsmc': (11, 'Supply Chain Fragility', 'critical'),
        'supply chain': (7, 'Economic Depletion', 'warning'),
        'supply shock': (7, 'Economic Depletion', 'critical'),
        'coordination': (10, 'Coordination Failure', 'critical'),
        'infrastructure': (8, 'Infrastructure Brittleness', 'warning'),
        'electrical grid': (2, 'Energy Infrastructure Failure', 'critical'),
        'power grid': (2, 'Energy Infrastructure Failure', 'critical'),
        'water': (1, 'Water Scarcity', 'critical'),
        'drought': (1, 'Water Scarcity', 'critical'),
        'energy': (2, 'Energy Infrastructure Failure', 'warning'),
        'food': (5, 'Feedback Amplification', 'critical'),
        'fertilizer': (5, 'Feedback Amplification', 'critical'),
        'rare earth': (9, 'Material Constraints', 'warning'),
        'measurement': (6, 'Measurement Blindness', 'warning'),
        'institutional': (3, 'Institutional Lag', 'warning'),
        'feedback': (5, 'Feedback Amplification', 'critical'),
        'bifurcation': (13, 'Bifurcation Risk', 'critical'),
        'tipping point': (13, 'Bifurcation Risk', 'critical'),
        'geopolitical': (4, 'Geopolitical Shock', 'critical'),
        'conflict': (4, 'Geopolitical Shock', 'critical'),
        'sanction': (4, 'Geopolitical Shock', 'warning'),
    }

    # Extract content for analysis
    body_lower = email_body.lower()
    subject_lower = email_subject.lower()
    content = f"{subject_lower} {body_lower}"

    # Find identified nodes and mechanisms
    identified_signals = {}
    for keyword, (node_id, mechanism, severity) in cascade_keywords.items():
        if keyword in content:
            if node_id not in identified_signals:
                identified_signals[node_id] = {
                    'mechanism': mechanism,
                    'severity': severity,
                    'keywords': [keyword]
                }
            else:
                identified_signals[node_id]['keywords'].append(keyword)

    # Extract metrics and numbers
    metrics = re.findall(r'(\d+[\.,]\d+%?|\d+\s*(?:billion|million|trillion|weeks?|months?|years?))', email_body, re.IGNORECASE)
    metric_str = ', '.join(metrics[:3]) if metrics else ''

    # Create signals for each identified node
    if identified_signals:
        for node_id, info in identified_signals.items():
            signal = {
                'node': node_id,
                'domain': 'Substack Research',
                'description': f"{email_subject} (by {author})" + (f" [{metric_str}]" if metric_str else ""),
                'severity': info['severity'],
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': f'Substack: {author}'
            }
            signals.append(signal)

            # Create corresponding finding
            finding = {
                'mechanism': info['mechanism'],
                'text': f"{email_subject}: {email_body[:300]}",  # Slightly longer excerpt
                'confidence': 0.8,  # Adjusted for Substack research source
                'evidence': f'Substack newsletter from {author} on {datetime.now().strftime("%Y-%m-%d")}'
            }
            findings.append(finding)
    else:
        # Fallback: create general research signal if no specific nodes found
        signal = {
            'node': 6,  # Default to Measurement/Analysis node
            'domain': 'Substack Research',
            'description': f"{email_subject} (by {author})",
            'severity': 'info',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': f'Substack: {author}'
        }
        signals.append(signal)

        finding = {
            'mechanism': 'General Research Finding',
            'text': f"{email_subject}: {email_body[:300]}",
            'confidence': 0.7,
            'evidence': f'Substack newsletter from {author}'
        }
        findings.append(finding)

    return signals, findings

def import_substack_signals(emails_data):
    """
    Import signals and findings from list of Substack emails.

    emails_data format:
    [
        {
            'author': 'Scientist Name',
            'subject': 'Email subject line',
            'body': 'Email body content',
            'date': '2026-08-19'
        },
        ...
    ]
    """

    signal_count = 0
    finding_count = 0

    for email in emails_data:
        try:
            author = email.get('author', 'Unknown')
            subject = email.get('subject', 'Untitled')
            body = email.get('body', '')

            signals, findings = parse_substack_email(subject, body, author)

            # Add signals to database
            for signal in signals:
                try:
                    add_signal(
                        signal['node'],
                        signal['domain'],
                        signal['description'],
                        signal['severity'],
                        signal['date'],
                        signal['source']
                    )
                    signal_count += 1
                except Exception as e:
                    print(f"⚠ Error adding signal from {author}: {e}")

            # Add findings to database
            for finding in findings:
                try:
                    add_finding(
                        finding['mechanism'],
                        finding['text'],
                        finding['confidence'],
                        supporting_evidence=finding['evidence']
                    )
                    finding_count += 1
                except Exception as e:
                    print(f"⚠ Error adding finding from {author}: {e}")

        except Exception as e:
            print(f"✗ Error processing email from {email.get('author', 'Unknown')}: {e}")

    return signal_count, finding_count

def main():
    print("\n" + "="*60)
    print("📧 Importing Substack Signals")
    print("   Global Critical Infrastructure Research")
    print("="*60 + "\n")

    # Fetch real emails from Gmail Substack folder
    print("🔍 Connecting to Gmail...")
    emails_data = fetch_substack_emails_from_gmail(max_results=20)

    if not emails_data:
        print("ℹ No Substack emails found in Gmail")
        print("   Next steps:")
        print("   1. Create a Gmail label 'Substack'")
        print("   2. Label your Substack emails with it")
        print("   3. Re-run this script")
        print("\n" + "="*60 + "\n")
        return

    print(f"\n📊 Processing {len(emails_data)} emails...\n")
    signal_count, finding_count = import_substack_signals(emails_data)

    print(f"\n✅ Import complete!")
    print(f"   • Signals added: {signal_count}")
    print(f"   • Findings added: {finding_count}")
    print(f"   • Total entries: {signal_count + finding_count}")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
