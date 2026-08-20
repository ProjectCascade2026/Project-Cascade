#!/usr/bin/env python3
"""
Account Switcher for Project Cascade
Allows quick switching between Google accounts (new vs. old if recovered)
"""

import json
import sys

CONFIG_PATH = "cascade_config.json"

def switch_account(account_email):
    """Switch active Google account in config"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

        # Validate account is in config
        if account_email not in [config["google_account"]["active_account"],
                                  config["google_account"]["fallback_account"]]:
            print(f"❌ Error: Account {account_email} not in config")
            return False

        # Switch active account
        old_account = config["google_account"]["active_account"]
        config["google_account"]["active_account"] = account_email
        config["mcp_authentication"]["account_email"] = account_email

        # Save config
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✓ Switched from {old_account} → {account_email}")
        print(f"✓ Restart cascade_app.py for changes to take effect")
        return True

    except FileNotFoundError:
        print(f"❌ Error: {CONFIG_PATH} not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_status():
    """Show current active account"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

        active = config["google_account"]["active_account"]
        fallback = config["google_account"]["fallback_account"]
        print(f"📍 Active Account:  {active}")
        print(f"🔄 Fallback Account: {fallback}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        account = sys.argv[1]
        switch_account(account)
    else:
        show_status()
