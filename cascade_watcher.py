# -*- coding: utf-8 -*-
"""
File Watcher - Auto-update database when markdown files change
Uses watchdog to monitor file changes
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cascade_importer import (
    import_cascade_nodes, import_from_confluence_state,
    import_cascade_sequences, import_baseline_failures,
    import_signals_from_confluence, import_signals_from_cascading_nodes_log,
    import_signals_from_dan_evidence, import_daily_findings, import_amplitude_watch
)

CONFLUENCE_DIR = Path(__file__).parent
# Only watch daily updates and escalation tracking
# Signal source files (confluence_state.md, CASCADING_NODES_WATCH_LOG.md, etc)
# are batch-imported once at startup; re-importing them would create duplicates
WATCH_FILES = {
    'daily_findings.md': import_daily_findings,
    'AMPLITUDE_WATCH_LOG.md': import_amplitude_watch,
}

class CascadeFileHandler(FileSystemEventHandler):
    """Handler for cascade file changes"""

    def on_modified(self, event):
        if event.is_directory:
            return

        filename = Path(event.src_path).name

        if filename in WATCH_FILES:
            print(f"\n🔄 {filename} changed, updating database...")
            try:
                WATCH_FILES[filename]()
                print(f"✓ {filename} reimported successfully")
            except Exception as e:
                print(f"⚠ Error reimporting {filename}: {e}")

def start_watcher():
    """Start file watcher"""
    event_handler = CascadeFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(CONFLUENCE_DIR), recursive=False)
    observer.start()

    print(f"\n👁️  Watching for changes in {CONFLUENCE_DIR}")
    print("   Files being monitored:")
    for filename in WATCH_FILES:
        print(f"     • {filename}")
    print("\nPress Ctrl+C to stop watching.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n⏹ Watcher stopped")

    observer.join()

if __name__ == '__main__':
    start_watcher()
