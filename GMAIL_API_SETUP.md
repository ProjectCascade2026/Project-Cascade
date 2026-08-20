# Gmail API Setup Guide

This guide explains how to set up Gmail API authentication for the Substack email ingestion pipeline.

## One-Time Setup (First Run)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a Project" → "New Project"
3. Enter project name: `ProjectCascade` (or your preference)
4. Click "Create"
5. Wait for project to be created

### Step 2: Enable Gmail API

1. In Google Cloud Console, search for "Gmail API"
2. Click "Gmail API" in the results
3. Click "Enable"
4. Wait for the API to be enabled

### Step 3: Create OAuth2 Desktop Credentials

1. In Google Cloud Console, go to "Credentials" (left sidebar)
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, click "Configure OAuth consent screen"
   - Select "External" user type
   - Fill in app name: `ProjectCascade`
   - Add your email as a test user
   - Click "Save and Continue" through all screens
4. Back on Credentials page, click "Create Credentials" → "OAuth client ID" again
5. Select "Desktop app" as application type
6. Click "Create"
7. Click "Download" button (down arrow icon)
8. Save the file as `credentials.json` in your `cascade_app_package` folder

### Step 4: Prepare Gmail Folder

1. Open Gmail in your browser
2. Create a label called "Substack" if you haven't already
3. Label any existing Substack emails with the "Substack" label
4. All future Substack emails should be labeled with "Substack"

## Running the Import Script

### First Run (Will Authenticate)

```bash
cd C:\Users\Dr. Strangelove\cascade_app_package
python import_substack_signals.py
```

On first run:
1. A browser window will open asking you to authorize the app
2. Click "Allow" to grant access to Gmail
3. The script will automatically save a token to `token.pickle`
4. Substack emails will be imported into the database

### Subsequent Runs

```bash
python import_substack_signals.py
```

The script will automatically use the saved `token.pickle` token without requiring re-authorization.

## What Gets Imported

The script extracts:
- **Signals**: Infrastructure alerts organized by cascade node (semiconductors, energy, water, food, etc.)
- **Findings**: Research insights organized by cascade mechanism with confidence levels
- **Source Attribution**: Each signal/finding notes the Substack author and publication date

## Troubleshooting

### "Missing credentials.json"

**Problem**: Script says credentials.json is missing

**Solution**: Make sure you downloaded `credentials.json` from Google Cloud Console and saved it in the `cascade_app_package` folder

### "Substack label not found in Gmail"

**Problem**: Script can't find the Substack folder in Gmail

**Solution**: 
1. Go to Gmail
2. Create a label called "Substack"
3. Label at least one test email with it
4. Re-run the script

### "Invalid grant" or "token expired"

**Problem**: Token authentication fails after several days

**Solution**: Delete `token.pickle` and re-run the script to re-authenticate with Gmail

## Files Modified/Created

- `import_substack_signals.py` — Main ingestion script with Gmail API integration
- `requirements.txt` — Added Gmail API dependencies
- `credentials.json` — Created by you from Google Cloud Console (DO NOT COMMIT TO GIT)
- `token.pickle` — Created automatically on first run (DO NOT COMMIT TO GIT)

## Security Notes

⚠️ **Important**: `credentials.json` and `token.pickle` are sensitive files:
- Add them to `.gitignore` (already done for `token.pickle`)
- Add `credentials.json` to `.gitignore` if not already present
- Never commit these files to GitHub
- They're listed in the `.gitignore` file for safety

## Next Steps

1. Set up credentials.json as described above
2. Run: `python import_substack_signals.py`
3. Check that emails were imported successfully
4. Optional: Set up a scheduled task to run the import daily (see below)

## Scheduled Daily Import (Optional)

To automatically fetch and import Substack emails daily:

### Windows Task Scheduler

1. Open Task Scheduler (search "Task Scheduler" in Start menu)
2. Click "Create Basic Task..."
3. Name: `ImportSubstackSignals`
4. Trigger: Daily at preferred time (e.g., 8:00 AM)
5. Action:
   - Program: `python`
   - Arguments: `C:\Users\Dr. Strangelove\cascade_app_package\import_substack_signals.py`
   - Start in: `C:\Users\Dr. Strangelove\cascade_app_package`
6. Click "Finish"

The script will now run automatically each day and import any new Substack emails.

## Questions?

Refer to [Google API Documentation](https://developers.google.com/gmail/api) for more details.
