# Automated Substack Import Setup

Set this up once, then Substack emails are imported automatically **every day** with zero manual intervention.

## 3-Step Setup (10 minutes)

### Step 1: Create Secure Config File

Create a new file: `C:\Users\Dr. Strangelove\cascade_app_package\config.ini`

**Copy this exactly:**

```ini
[gmail]
email = dr.stranelove@gmail.com
app_password = mthpgaqnysjrqdwt
```

Replace the email and password with YOUR credentials.

**IMPORTANT:** This file is in `.gitignore` — it will NEVER be committed to GitHub.

### Step 2: Test the Script

Run once to verify it works:

```bash
python import_substack_imap.py
```

You should see:
```
✅ Authenticated as dr.stranelove@gmail.com
✅ Opened folder: Substack
✅ Fetched X emails from Substack
```

No user input needed — it reads from `config.ini` automatically.

### Step 3: Schedule Daily Import with Windows Task Scheduler

**Open Task Scheduler:**
1. Press `Win + R`
2. Type `taskschd.msc` → Enter
3. Click "Create Basic Task..."

**Configure the task:**

| Field | Value |
|-------|-------|
| **Name** | `Import Substack Emails` |
| **Description** | Daily import of Substack research into Project Cascade |
| **Trigger** | Daily at 8:00 AM (or your preferred time) |
| **Action** | Start a program |
| **Program** | `C:\Python39\python.exe` |
| **Arguments** | `C:\Users\Dr. Strangelove\cascade_app_package\import_substack_imap.py` |
| **Start in** | `C:\Users\Dr. Strangelove\cascade_app_package` |

**Detailed steps:**

1. **General tab:**
   - Name: `Import Substack Emails`
   - Check: "Run whether user is logged in or not"

2. **Trigger tab:**
   - Click "New"
   - Begin the task: "On a schedule"
   - Set to: "Daily"
   - Start time: `8:00:00 AM` (or your preference)
   - Click "OK"

3. **Action tab:**
   - Click "New"
   - Action: "Start a program"
   - Program/script: `C:\Python39\python.exe`
   - Add arguments: `import_substack_imap.py`
   - Start in: `C:\Users\Dr. Strangelove\cascade_app_package`
   - Click "OK"

4. **Conditions tab (optional):**
   - Uncheck "Stop the task if it runs longer than:"
   - (Allows the task to run until it completes)

5. **Settings tab:**
   - Check: "Run task as soon as possible after a scheduled start is missed"
   - Click "OK"

## How It Works

**Every day at 8:00 AM:**
1. Windows Task Scheduler launches Python
2. Script reads credentials from `config.ini`
3. Connects to Gmail via IMAP
4. Fetches Substack emails from your "Substack" folder
5. Extracts cascade signals and findings
6. Adds them to your database
7. Dashboard automatically reflects new research

**Zero user interaction needed.**

## Verification

### Test the scheduled task immediately:

1. Open Task Scheduler
2. Find "Import Substack Emails"
3. Right-click → "Run"
4. Wait for it to complete
5. Check your dashboard for new research

### Check logs (if something goes wrong):

Scheduled tasks output goes to Windows Event Viewer:
- Open "Event Viewer"
- Navigate: Windows Logs → Application
- Look for Python or task execution logs

## Updating Credentials

If you need to change your app password:

1. Update `config.ini` with new credentials
2. Task Scheduler will pick it up automatically next run

## Files Involved

| File | Purpose |
|------|---------|
| `import_substack_imap.py` | Main import script (reads from config.ini) |
| `config.ini` | Your Gmail credentials (NOT in git) |
| `import_substack_signals.py` | Signal extraction & parsing |
| `cascade_db.py` | Database storage |

## Troubleshooting

### "config.ini not found"
- Make sure you created the file in the cascade_app_package folder
- File should be at: `C:\Users\Dr. Strangelove\cascade_app_package\config.ini`

### Task runs but no emails imported
- Manually run `python import_substack_imap.py` to see error messages
- Task Scheduler suppresses output, so manual run shows what went wrong

### Task doesn't run at scheduled time
- Check that Task Scheduler is set to run the task
- Verify your Python path is correct: `C:\Python39\python.exe`
- Make sure the cascade_app_package folder path is correct

## Security Notes

✅ **Good practices:**
- `config.ini` is in `.gitignore` — never committed to GitHub
- App password is revocable at any time in Google Account settings
- Task runs in background with no user interaction
- Credentials stored only locally, not in cloud

⚠️ **Never:**
- Share `config.ini` with anyone
- Commit `config.ini` to version control
- Post your app password online

## Next Steps

1. Create `config.ini` with your Gmail credentials
2. Test: `python import_substack_imap.py`
3. Set up Task Scheduler for daily runs
4. Monitor dashboard for new research appearing each day

Done! Your cascade research pipeline is fully automated.
