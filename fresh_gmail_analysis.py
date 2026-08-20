#!/usr/bin/env python3
"""
Fresh Gmail analysis - processes ALL messages against PROJECT GOALS
Ignores previous analysis status, forces re-evaluation
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
import re

# Import cascade functions
import sys
sys.path.insert(0, '.')

try:
    from cascade_db import add_signal, add_finding, get_all_goals
except ImportError:
    print("Error: cascade_db.py not found")
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
    """Fetch ALL messages from INBOX (not just unanalyzed)"""
    print("\n[IMAP] Connecting to Gmail IMAP...")
    
    messages_data = []
    
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_user, app_password)
        print(f"Authenticated as {gmail_user}")
        
        # Select INBOX only
        mail.select('INBOX', readonly=True)
        print("\n[INBOX] Fetching all messages from INBOX...")
        
        # Fetch ALL messages
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        
        print(f"Found {len(email_ids)} total messages in INBOX")
        
        for i, email_id in enumerate(email_ids):
            if i % 5 == 0:
                print(f"  Processing {i}/{len(email_ids)}...", end='\r')
            
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    try:
                        msg = email.message_from_bytes(response_part[1])
                        
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
                            'author': author,
                            'subject': subject,
                            'body': body,
                            'date': date_formatted
                        })
                    except Exception as e:
                        continue
        
        mail.close()
        mail.logout()
        
        print(f"\nFetched {len(messages_data)} messages                    ")
        return messages_data
    
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_against_goals(subject, body, author):
    """
    Analyze email content against PROJECT GOALS
    Returns signals and findings with goal-relevance scoring
    """
    signals = []
    findings = []
    
    # Get project goals
    try:
        goals = get_all_goals()
    except:
        goals = []
    
    if not goals:
        print("    [WARNING] No goals in database")
        return signals, findings
    
    # Combine and normalize content
    content = f"{subject} {body}".lower()
    
    # Track goal matches
    goal_matches = {}
    
    for goal in goals:
        goal_text = goal['goal_text'].lower()
        match_count = 0
        matched_keywords = []
        
        # Check for keyword matches
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
    
    # Extract signals for matching goals
    for goal_id, data in goal_matches.items():
        goal = data['goal']
        matches = data['matches']
        keywords = data['keywords']
        
        severity = 'critical' if matches >= 3 else 'warning' if matches >= 2 else 'info'
        
        signal = {
            'node': 6,  # Default to infrastructure system
            'domain': f"Goal Match: {goal['category'].upper()}",
            'description': f"Email from {author} matches goal keywords: {', '.join(keywords[:3])}. Subject: {subject}",
            'severity': severity,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': f"Gmail INBOX: {subject[:40]}"
        }
        signals.append(signal)
    
    # Generate finding if good goal relevance
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
    print("FRESH GMAIL ANALYSIS - ALL INBOX MESSAGES")
    print("="*70 + "\n")
    
    # Load credentials
    gmail_user, app_password = load_config()
    if not gmail_user:
        print("Cannot proceed without config.ini")
        return
    
    # Fetch all inbox messages
    messages_data = fetch_all_inbox_messages(gmail_user, app_password)
    
    if not messages_data:
        print("\nNo messages found")
        return
    
    print(f"\n[ANALYSIS] Analyzing {len(messages_data)} messages against project goals...\n")
    
    signal_count = 0
    finding_count = 0
    goal_match_count = 0
    
    for i, msg in enumerate(messages_data):
        try:
            signals, findings = analyze_against_goals(msg['subject'], msg['body'], msg['author'])
            
            if signals:
                for signal in signals:
                    try:
                        add_signal(signal['node'], signal['domain'], signal['description'],
                                  signal['severity'], signal['date'], signal['source'])
                        signal_count += 1
                        goal_match_count += 1
                    except Exception as e:
                        pass
            
            if findings:
                for finding in findings:
                    try:
                        add_finding(finding['mechanism'], finding['text'],
                                   finding['confidence'], finding['evidence'])
                        finding_count += 1
                    except Exception as e:
                        pass
            
            if (i+1) % 5 == 0:
                print(f"  Processed {i+1}/{len(messages_data)} messages | Signals: {signal_count} | Findings: {finding_count}")
        
        except Exception as e:
            pass
    
    print(f"\n" + "="*70)
    print("FRESH ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nResults:")
    print(f"  - Total messages analyzed: {len(messages_data)}")
    print(f"  - Messages with goal matches: {goal_match_count}")
    print(f"  - Signals extracted: {signal_count}")
    print(f"  - Findings generated: {finding_count}")
    print(f"\n  All results added to cascade database (signals + research_findings tables)")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
