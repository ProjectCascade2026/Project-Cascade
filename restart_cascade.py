#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Cascade Auto-Restart Utility
Kills running Streamlit process and restarts the app
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def kill_streamlit():
    """Kill any running Streamlit processes"""
    print("🛑 Stopping Streamlit...")

    # Windows: use taskkill
    if sys.platform == "win32":
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "streamlit.exe"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✓ Streamlit process terminated")
        else:
            print("   ℹ No Streamlit process found")
    else:
        # Linux/Mac: use pkill
        result = subprocess.run(
            ["pkill", "-f", "streamlit"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✓ Streamlit process terminated")
        else:
            print("   ℹ No Streamlit process found")

def restart_cascade():
    """Restart the Cascade app"""
    cascade_dir = Path(__file__).parent
    os.chdir(cascade_dir)

    print("\n⏳ Waiting 2 seconds before restart...\n")
    time.sleep(2)

    print("🚀 Restarting Project Cascade...\n")
    subprocess.call([
        sys.executable, 'launcher.py'
    ])

def main():
    """Main restart flow"""
    print("\n" + "=" * 50)
    print("🔄 Project Cascade Auto-Restart")
    print("=" * 50 + "\n")

    try:
        kill_streamlit()
        restart_cascade()
    except KeyboardInterrupt:
        print("\n\n⏹ Restart cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
