#!/usr/bin/env python3
"""
Diagnose project goals in database
"""

import sys
import os
import sqlite3

cascade_path = os.path.expanduser("~/cascade_app_package")
sys.path.insert(0, cascade_path)

db_path = os.path.join(cascade_path, "cascade_data.db")

print("\n" + "="*60)
print("Project Goals Diagnostic")
print("="*60 + "\n")

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Get all goals (regardless of status)
    c.execute('SELECT * FROM project_goals ORDER BY goal_id')
    all_goals = c.fetchall()

    print(f"Total goals in database: {len(all_goals)}\n")

    if all_goals:
        for goal in all_goals:
            print(f"[ID {goal['goal_id']}] Status: {goal['status']} | Category: {goal['category']}")
            print(f"  Text: {goal['goal_text'][:80]}...")
            print(f"  Created: {goal['created_date']}")
            if goal['retired_date']:
                print(f"  Retired: {goal['retired_date']}")
            print()
    else:
        print("NO GOALS FOUND IN DATABASE!")

    # Count by status
    c.execute('SELECT status, COUNT(*) as count FROM project_goals GROUP BY status')
    status_counts = c.fetchall()

    print("\nGoals by status:")
    for row in status_counts:
        print(f"  {row['status']}: {row['count']}")

    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
