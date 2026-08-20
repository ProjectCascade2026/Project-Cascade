#!/usr/bin/env python3
"""
Count total emails in Gmail across all folders
"""

import imaplib
import configparser
import os

def count_gmail_emails():
    """Count total emails in all Gmail folders"""
    
    # Load credentials from config.ini
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("config.ini not found")
        return
    
    config.read('config.ini')
    try:
        gmail_user = config.get('gmail', 'email')
        app_password = config.get('gmail', 'app_password')
    except:
        print("Invalid config.ini format")
        return
    
    print("\n" + "="*60)
    print(f"Counting Gmail emails for {gmail_user}")
    print("="*60 + "\n")
    
    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_user, app_password)
        print(f"Authenticated as {gmail_user}\n")
        
        # Get all folders
        status, mailbox_list = mail.list()
        
        total_emails = 0
        folder_counts = {}
        
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
                
                # Count emails
                status, messages = mail.search(None, 'ALL')
                email_count = len(messages[0].split())
                
                folder_counts[folder_name] = email_count
                total_emails += email_count
                
                print(f"  {folder_name}: {email_count} emails")
            except Exception as e:
                print(f"  {folder_name}: ERROR - {e}")
        
        mail.close()
        mail.logout()
        
        print("\n" + "="*60)
        print(f"TOTAL: {total_emails} emails across all folders")
        print("="*60 + "\n")
        
        return total_emails
    
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == '__main__':
    count_gmail_emails()
