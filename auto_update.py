#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Cascade Auto-Update Manager
Syncs files, cleans database/cache, and restarts the app
"""

import subprocess
import sys
import time
import os
import shutil
from pathlib import Path

def kill_streamlit():
    """Kill any running Streamlit processes"""
    print("🛑 Stopping Streamlit...")

    if sys.platform == "win32":
        # Windows: use taskkill with multiple passes to ensure all processes die
        subprocess.run(["taskkill", "/F", "/IM", "streamlit.exe"], capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        time.sleep(2)
        # Second pass to catch any lingering processes
        subprocess.run(["taskkill", "/F", "/IM", "streamlit.exe"], capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
    else:
        # Linux/Mac: use pkill
        subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        subprocess.run(["pkill", "-f", "launcher"], capture_output=True)

    time.sleep(3)
    print("   ✓ Streamlit stopped")

def clean_database_and_cache():
    """Remove database and Python cache to force fresh import"""
    cascade_dir = Path(__file__).parent
    os.chdir(cascade_dir)

    # Delete database with retry logic
    db_file = cascade_dir / 'cascade_data.db'
    if db_file.exists():
        max_retries = 5
        for attempt in range(max_retries):
            try:
                db_file.unlink()
                print("   ✓ Database cleared")
                break
            except OSError as e:
                if attempt < max_retries - 1:
                    print(f"   ⏳ Retrying database deletion (attempt {attempt + 2}/{max_retries})...")
                    time.sleep(2)
                else:
                    print(f"   ⚠ Warning: Could not delete database after {max_retries} attempts")
                    print(f"   Manual deletion may be required: {db_file}")

    # Delete __pycache__
    pycache_dir = cascade_dir / '__pycache__'
    if pycache_dir.exists():
        shutil.rmtree(pycache_dir, ignore_errors=True)
        print("   ✓ Cache cleared")

    # Delete .pyc files
    for pyc in cascade_dir.glob('*.pyc'):
        try:
            pyc.unlink()
        except:
            pass

def restart_launcher():
    """Restart the launcher in background"""
    cascade_dir = Path(__file__).parent
    os.chdir(cascade_dir)

    print("\n🚀 Restarting Project Cascade...\n")

    if sys.platform == "win32":
        # Windows: start in separate process
        subprocess.Popen([sys.executable, 'launcher.py'])
    else:
        # Linux/Mac: start in separate process
        subprocess.Popen([sys.executable, 'launcher.py'])

    print("   ✓ Launcher started in background")
    print("   📊 Dashboard will be ready in ~30 seconds at http://localhost:8501")

def main():
    """Main update flow"""
    print("\n" + "=" * 60)
    print("🔄 Project Cascade Auto-Update")
    print("=" * 60 + "\n")

    try:
        kill_streamlit()
        print("\n🧹 Cleaning up...")
        clean_database_and_cache()
        print("\n⏳ Waiting 2 seconds before restart...\n")
        time.sleep(2)
        restart_launcher()
        print("\n" + "=" * 60)
        print("✅ Update complete! Refreshing your browser...")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\n⏹ Update cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during update: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
