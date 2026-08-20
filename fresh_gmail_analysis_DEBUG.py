#!/usr/bin/env python3
"""
Fresh Gmail analysis - DEBUG version with error reporting
"""

import sys
import subprocess

try:
    from imap_tools import MailBox
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "imap-tools", "-q"])

import imaplib
import email
from email.header import decode_header
import configparser
import os
from datetime import datetime

# Import cascade functions
try:
    from cascade_db import add_signal, add_finding, get_all_goals
except ImportError as e:
    print(f"Error importing cascade_db: {e}")
    sys.exit(1)

def load_config():
    """Load Gmail credentials from config.ini"""
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("config.ini not found")
        return None, None
    
    config.read('config.ini')
    try:
        gmail_user = config.get('gmail', 'email')
        app_password = config.get('gmail', 'app_password')
        return gmail_user, app_password
    except:
        print("Invalid config.ini format")
        return None, None

def fetch_all_inbox_messages(gmail_user, app_password):
    """Fetch ALL messages from INBOX"""
    messages_data = []
    
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_user, app_password)
        print(f"Authenticated as {gmail_user}\n")
        
        mail.select('INBOX', readonly=True)
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        
        print(f"Found {len(email_ids)} total messages in INBOX\n")
        
        for i, email_id in enumerate(email_ids):
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    try:
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject = msg.get('Subject', 'Untitled')
                        from_addr = msg.get('From', 'Unknown')
                        date_str = msg.get('Date', '')
                        
                        author = from_addr.split('<')[0].strip() if '<' in from_addr else from_addr
                        
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
                        
                        try:
                            from email.utils import parsedate_to_datetime
                            dt = parsedate_to_datetime(date_str)
                            date_formatted = dt.strftime('%Y-%m-%d')
                        except:
                            date_formatted = datetime.now().strftime('%Y-%m-%d')
                        
                        messages_data.append({
                            'author': author,
                            'subject': subject,
                            'body': body,
                            'date': date_formatted
                        })
                    except Exception as e:
                        print(f"  [ERROR parsing message {i}]: {e}")
        
        mail.close()
        mail.logout()
        
        print(f"Fetched {len(messages_data)} messages successfully\n")
        return messages_data
    
    except Exception as e:
        print(f"IMAP Error: {e}")
        return []

def analyze_against_goals(subject, body, author):
    """Analyze email content against PROJECT GOALS"""
    signals = []
    findings = []
    
    try:
        goals = get_all_goals()
    except Exception as e:
        print(f"    [ERROR getting goals]: {e}")
        return signals, findings
    
    if not goals:
        return signals, findings
    
    content = f"{subject} {body}".lower()
    goal_matches = {}
    
    for goal in goals:
        goal_text = goal['goal_text'].lower()
        match_count = 0
        matched_keywords = []
        
        goal_keywords = [w for w in goal_text.split() if len(w) > 4]
        for keyword in goal_keywords:
            if keyword in content:
                match_count += 1
                matched_keywords.append(keyword)
        
        if match_count > 0:
            goal_matches[goal['goal_id']] = {
                'goal': goal,
                'matches': match_count,
                'keywords': matched_keywords
            }
    
    for goal_id, data in goal_matches.items():
        goal = data['goal']
        matches = data['matches']
        keywords = data['keywords']
        
        severity = 'critical' if matches >= 3 else 'warning' if matches >= 2 else 'info'
        
        signal = {
            'node': 6,
            'domain': f"Goal Match: {goal['category'].upper()}",
            'description': f"Email from {author} matches goal keywords: {', '.join(keywords[:3])}. Subject: {subject}",
            'severity': severity,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': f"Gmail INBOX: {subject[:40]}"
        }
        signals.append(signal)
    
    if goal_matches and len(body) > 100:
        top_goals = sorted(goal_matches.items(), key=lambda x: x[1]['matches'], reverse=True)[:2]
        goal_refs = ', '.join([g[1]['goal']['goal_text'][:35] for g in top_goals])
        
        finding = {
            'mechanism': 'Email-Goal Alignment',
            'text': f"From {author}: Relevant to {goal_refs}. Subject: {subject}. Key content: {body[:200]}...",
            'confidence': min(0.95, 0.6 + (len(goal_matches) * 0.15)),
            'evidence': f"Keyword matches across {len(goal_matches)} project goals"
        }
        findings.append(finding)
    
    return signals, findings

def main():
    print("\n" + "="*70)
    print("FRESH GMAIL ANALYSIS - DEBUG VERSION")
    print("="*70 + "\n")
    
    gmail_user, app_password = load_config()
    if not gmail_user:
        return
    
    messages_data = fetch_all_inbox_messages(gmail_user, app_password)
    
    if not messages_data:
        print("No messages to analyze")
        return
    
    print(f"[ANALYSIS] Analyzing {len(messages_data)} messages...\n")
    
    signal_count = 0
    finding_count = 0
    error_count = 0
    
    for i, msg in enumerate(messages_data):
        try:
            signals, findings = analyze_against_goals(msg['subject'], msg['body'], msg['author'])
            
            if signals:
                for signal in signals:
                    try:
                        result = add_signal(signal['node'], signal['domain'], signal['description'],
                                          signal['severity'], signal['date'], signal['source'])
                        print(f"  [OK] Signal {signal_count+1} added (ID: {result})")
                        signal_count += 1
                    except Exception as e:
                        print(f"  [ERROR adding signal]: {str(e)[:80]}")
                        error_count += 1
            
            if findings:
                for finding in findings:
                    try:
                        result = add_finding(finding['mechanism'], finding['text'],
                                           finding['confidence'], finding['evidence'])
                        print(f"  [OK] Finding {finding_count+1} added (ID: {result})")
                        finding_count += 1
                    except Exception as e:
                        print(f"  [ERROR adding finding]: {str(e)[:80]}")
                        error_count += 1
        
        except Exception as e:
            print(f"  [ERROR processing message {i}]: {str(e)[:80]}")
            error_count += 1
    
    print(f"\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nResults:")
    print(f"  - Signals added to database: {signal_count}")
    print(f"  - Findings added to database: {finding_count}")
    print(f"  - Errors encountered: {error_count}")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
