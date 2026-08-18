# Project Cascade — Local Setup Guide

## Installation & Setup

### Step 1: Prerequisites

You need Python 3.8 or higher installed on your machine.

Check your Python version:
```bash
python3 --version
```

### Step 2: Extract Files

Extract all files from this package to a directory on your computer, e.g.:
```
~/Projects/cascade/
├── cascade_db.py
├── cascade_importer.py
├── cascade_watcher.py
├── cascade_app.py
├── launcher.py
├── CASCADE_APP_README.md
└── (this file)
```

### Step 3: Install Dependencies

Open terminal/command prompt in the cascade directory and run:

```bash
pip install streamlit pandas plotly watchdog
```

Or let the launcher install them automatically (see below).

### Step 4: Import Your Data Files

Copy these markdown files into the same directory as the Python scripts:
```
confluence_state.md
CASCADING_NODES_WATCH_LOG.md
BASELINE_RETURN_FAILURE_RESEARCH_20260818.md
DAN_CASCADE_MECHANISM_EVIDENCE_20260818.md
```

The importer will automatically find and parse them.

### Step 5: Launch the Application

**On macOS/Linux:**
```bash
python3 launcher.py
```

**On Windows:**
```bash
python launcher.py
```

### Step 6: Open Dashboard

The terminal will display:
```
📊 Opening Streamlit dashboard at http://localhost:8501
```

Open your browser to: **http://localhost:8501**

---

## What Happens on First Run

1. ✅ Dependencies checked/installed
2. ✅ Database created (`cascade_data.db`)
3. ✅ Your markdown files parsed and imported
4. ✅ Streamlit dashboard launches
5. ✅ File watcher starts monitoring for changes

## File Watcher (Auto-Update)

The app monitors these files for changes:
- `confluence_state.md`
- `CASCADING_NODES_WATCH_LOG.md`
- `BASELINE_RETURN_FAILURE_RESEARCH_20260818.md`

**When you update any of these files**, the database automatically re-imports without restarting the app.

## Regular Usage

### Daily Workflow

1. **Start the app** once in the morning:
   ```bash
   python3 launcher.py
   ```

2. **Access dashboard** at `http://localhost:8501`

3. **Update your markdown files** as you work (add new signals, CASCADE observations, etc.)

4. **Dashboard auto-refreshes** without manual intervention

5. **Stop when done**:
   - Press `Ctrl+C` in the terminal
   - Close the browser tab

### Adding New Data

Update any of these files and the dashboard auto-updates:

**Add a signal**:
- Edit `confluence_state.md` or create new tracking

**Add a CASCADE sequence**:
- Edit `CASCADING_NODES_WATCH_LOG.md`

**Add baseline failure**:
- Edit `BASELINE_RETURN_FAILURE_RESEARCH_20260818.md`

---

## Database Location

The database file `cascade_data.db` will be created in the same directory as the Python scripts.

- **Size**: ~50-100KB (grows slowly)
- **Format**: SQLite (portable, no server needed)
- **Backup**: Just copy `cascade_data.db` to back up all data

---

## Troubleshooting

### "Module not found" errors

Run the installer:
```bash
pip install streamlit pandas plotly watchdog
```

### Dashboard won't load

1. Check terminal for errors
2. Ensure you're visiting `http://localhost:8501` (not https)
3. Wait 5-10 seconds after starting—Streamlit takes a moment to initialize

### File watcher not updating

The watcher monitors for file *saves*. Make sure you:
- **Save** the markdown files (Ctrl+S or Cmd+S)
- Wait 1-2 seconds
- Refresh browser (F5)

### Port already in use

If port 8501 is busy, Streamlit will try 8502, 8503, etc. Check the terminal output for the actual URL.

---

## Advanced: Manual Components

If you prefer to run components separately:

**Just the database + importer:**
```bash
python3 cascade_importer.py
```

**Just the file watcher:**
```bash
python3 cascade_watcher.py
```

**Just the Streamlit app:**
```bash
streamlit run cascade_app.py
```

---

## Support

If you encounter issues:

1. Check the terminal output for error messages
2. Ensure Python 3.8+ is installed
3. Verify markdown files are in the same directory
4. Try reinstalling dependencies: `pip install --upgrade streamlit pandas plotly watchdog`

---

## Application Architecture

```
User's Local Machine
├── cascade_app_package/ (your installation)
│   ├── cascade_db.py              # Database operations
│   ├── cascade_importer.py        # Imports markdown → database
│   ├── cascade_watcher.py         # Monitors file changes
│   ├── cascade_app.py             # Streamlit dashboard
│   ├── launcher.py                # Starts everything
│   ├── cascade_data.db            # Your data (SQLite)
│   └── confluence_*.md            # Your markdown files
└── Browser
    └── http://localhost:8501      # Dashboard view
```

**Key Benefit**: Everything runs locally. No cloud dependency. Data stays on your machine.

---

**Questions?** Check CASCADE_APP_README.md for more details about the 8 dashboard sections.

Happy tracking! 🚀
