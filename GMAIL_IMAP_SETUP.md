# Gmail IMAP Setup (No Google Cloud Required)

This is the **simplest way** to fetch Substack emails from Gmail. No console setup, no OAuth — just IMAP.

## Prerequisites

- Gmail account
- 2-factor authentication enabled (required for app passwords)

## One-Time Setup (5 minutes)

### Step 1: Enable 2-Factor Authentication

1. Go to https://myaccount.google.com/
2. Click "Security" (left sidebar)
3. Scroll to "How you sign in to Google"
4. Click "2-Step Verification" → "Get Started"
5. Follow the prompts to enable SMS/authenticator app
6. Done!

### Step 2: Create App-Specific Password

1. Go to https://myaccount.google.com/
2. Click "Security" (left sidebar)
3. Scroll to "How you sign in to Google"
4. Click "App passwords" (only appears if 2FA is enabled)
5. Select "Mail" and "Windows Computer"
6. Click "Generate"
7. Copy the **16-character password** shown
8. Save it somewhere safe (you'll only see it once)

Example: `abcd efgh ijkl mnop`

### Step 3: Label Substack Emails (Optional)

In Gmail:
1. Create a label called "Substack" if you haven't
2. Label your Substack emails with it
3. Future emails can be auto-labeled with filters

## Running the Import

### First Time

```bash
cd C:\Users\Dr. Strangelove\cascade_app_package
python import_substack_imap.py
```

It will ask:
- **Gmail address**: michael@strangelove.com
- **App password**: The 16-character code from Step 2 (without spaces)

Example:
```
Enter your Gmail address: michael@strangelove.com
Enter your app-specific password (16 chars): abcdefghijklmnop
```

The script will:
1. Connect to Gmail via IMAP
2. Find your "Substack" folder
3. Fetch the last 20 emails
4. Extract cascade signals and findings
5. Add them to your database

### Automate with Windows Task Scheduler

To run daily automatically:

1. **Create a batch file** named `run_import.bat`:

```batch
@echo off
cd C:\Users\Dr. Strangelove\cascade_app_package
python import_substack_imap.py < input.txt
```

2. **Create `input.txt`** with your credentials:

```
michael@strangelove.com
abcdefghijklmnop
```

3. **Open Task Scheduler** and create a task:
   - Name: `ImportSubstackEmails`
   - Trigger: Daily at preferred time
   - Action: Run `run_import.bat`

## Troubleshooting

### "IMAP login failed"

**Problem**: Username/password rejected

**Solutions**:
- Make sure you used the **16-character app password**, not your Google password
- Check that 2FA is actually enabled
- Verify you copied the app password correctly (no spaces)

### "Folder not found"

**Problem**: Script can't find the "Substack" folder

**Solution**: In Gmail, make sure you have a label called "Substack" and it has at least one email labeled with it

### "ConnectionError" or "timeout"

**Problem**: Can't connect to Gmail servers

**Solution**: 
- Check your internet connection
- Gmail IMAP servers might be temporarily down (rare)
- Try again in a few minutes

## Why IMAP Over OAuth?

- ✅ **No setup**: 2 steps, 5 minutes
- ✅ **No console**: No Google Cloud, no credentials files
- ✅ **Simple**: Standard IMAP protocol, widely supported
- ✅ **Secure**: App password is revocable at any time
- ❌ **Limitation**: Can't run on Streamlit Cloud (requires local credentials)

For Streamlit Cloud, you'd need OAuth (Google Cloud), but for local testing, IMAP is perfect.

## Next Steps

1. Enable 2FA on your Google Account
2. Create an app-specific password
3. Run: `python import_substack_imap.py`
4. Check your dashboard for new research findings
5. (Optional) Set up daily automation with Task Scheduler

Questions? Gmail IMAP is well-documented — search "Gmail IMAP setup" if you get stuck.
