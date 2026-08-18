#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Cascade Launcher
Standalone entry point for the application
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check and install required packages"""
    packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'watchdog': 'watchdog',
    }

    print("📦 Checking dependencies...\n")

    missing = []
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ⬇ {package_name} (will install)")
            missing.append(package_name)

    if missing:
        print(f"\n📥 Installing {len(missing)} package(s)...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-q', '--user'
        ] + missing)
        print("✓ Dependencies installed\n")
    else:
        print()

def main():
    """Main launcher"""
    confluence_dir = Path(__file__).parent

    print("\n🚀 Project Cascade Startup")
    print("=" * 50 + "\n")

    # Check dependencies
    check_dependencies()

    # Initialize database
    print("💾 Initializing database...")
    os.chdir(confluence_dir)

    from cascade_importer import initialize_and_import
    initialize_and_import()

    print("\n" + "=" * 50)
    print("\n✅ Ready to launch!")
    print("\n📊 Opening Streamlit dashboard at http://localhost:8501")
    print("   (Press Ctrl+C to stop)\n")

    # Launch Streamlit
    subprocess.call([
        sys.executable, '-m', 'streamlit', 'run',
        str(confluence_dir / 'cascade_app.py')
    ])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹ Shutdown requested")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
