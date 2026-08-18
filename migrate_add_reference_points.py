#!/usr/bin/env python3
"""
Migration: Add reference point metrics to existing database
Run this once to populate System Robustness baseline data
"""

from cascade_db import get_connection

def add_reference_points():
    """Add system robustness reference points if they don't exist"""
    conn = get_connection()
    c = conn.cursor()

    # Check if reference points already exist
    existing = c.execute('SELECT COUNT(*) FROM reference_points').fetchone()[0]

    if existing > 0:
        print("✓ Reference points already exist. Skipping migration.")
        conn.close()
        return

    reference_points = [
        ('System Robustness - Initial Baseline', 78.0, 'System Health', '2026-01-01'),
        ('System Robustness - Q1 2026', 72.5, 'System Health', '2026-03-31'),
        ('System Robustness - Q2 2026', 65.0, 'System Health', '2026-06-30'),
        ('System Robustness - Current', 58.0, 'System Health', '2026-08-18'),
    ]

    print("\n" + "="*60)
    print("📊 Adding Reference Points Migration")
    print("="*60 + "\n")

    count = 0
    for metric_name, value, category, date in reference_points:
        try:
            c.execute('''INSERT INTO reference_points (metric_name, value, category, date_recorded)
                         VALUES (?, ?, ?, ?)''',
                      (metric_name, value, category, date))
            print(f"✓ Added: {metric_name} = {value}%")
            count += 1
        except Exception as e:
            print(f"⚠ Error: {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ Migration complete! Added {count} reference points")
    print("   Restart the dashboard to see System Robustness metric update\n")

if __name__ == '__main__':
    add_reference_points()
