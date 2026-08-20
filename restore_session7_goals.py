#!/usr/bin/env python3
"""
Restore the 6 Session 7 project goals that are missing from database
"""

import sys
import os

cascade_path = os.path.expanduser("~/cascade_app_package")
sys.path.insert(0, cascade_path)

try:
    from cascade_db import add_goal, get_all_goals
except ImportError as e:
    print(f"ERROR: Could not import cascade_db: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Restoring Session 7 Project Goals")
print("="*60 + "\n")

# The 6 goals from Session 7 that should be in the database
session7_goals = [
    {
        "text": "Detect cascading system failures across global critical infrastructure before collapse becomes inevitable through autonomous multi-source monitoring",
        "category": "primary"
    },
    {
        "text": "Daily monitoring of critical infrastructure developments globally (food, commodities, ports, water, energy, geopolitics) with cascade implications",
        "category": "primary"
    },
    {
        "text": "Establish and maintain 4-routine autonomous data pipeline: news headlines, researcher perspectives, real-time infrastructure monitoring, institutional synthesis",
        "category": "supporting"
    },
    {
        "text": "Document all automated routines, data sources, and system architecture for transparency and cross-session continuity",
        "category": "supporting"
    },
    {
        "text": "Identify bifurcation points—moments when systems cross from recoverable stress to permanent failure—enabling early intervention",
        "category": "supporting"
    },
    {
        "text": "Map geographic bifurcation: track which regions survive infrastructure cascades vs. collapse based on self-sufficiency and dependencies",
        "category": "supporting"
    }
]

# Check current goals
existing_goals = get_all_goals(status=None)  # Get all, regardless of status
print(f"Current goals in database: {len(existing_goals)}\n")

# Add missing goals
added_count = 0
for goal_data in session7_goals:
    try:
        goal_id = add_goal(
            goal_text=goal_data["text"],
            category=goal_data["category"]
        )
        print(f"[OK] Added goal {goal_id}: {goal_data['category'].upper()}")
        print(f"     {goal_data['text'][:70]}...")
        added_count += 1
    except Exception as e:
        print(f"[ERROR] Failed to add goal: {e}")

print("\n" + "="*60)
print("Goal Restoration Complete")
print("="*60)

# Verify restoration
final_goals = get_all_goals(status=None)
print(f"\nTotal goals now in database: {len(final_goals)}")
print(f"New goals added: {added_count}")
print(f"\nActive goals by category:")

active_goals = get_all_goals()
categories = {}
for goal in active_goals:
    cat = goal.get('category', 'uncategorized')
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")

print()
