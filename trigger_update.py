#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote Update Trigger
Called by Claude to trigger auto-updates on the user's machine
This should be placed in a location accessible to the launcher
"""

import subprocess
import sys
import os
from pathlib import Path

def trigger_update():
    """Trigger the auto-update process"""
    cascade_dir = Path(__file__).parent
    os.chdir(cascade_dir)

    print("\n📡 Update triggered by Claude")
    print("Executing auto_update.py...\n")

    # Run auto_update in background
    if sys.platform == "win32":
        subprocess.Popen([sys.executable, 'auto_update.py'])
    else:
        subprocess.Popen([sys.executable, 'auto_update.py'])

    print("✓ Auto-update process started")

if __name__ == '__main__':
    trigger_update()
