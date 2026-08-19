#!/usr/bin/env python3
"""
Update Project Cascade goals based on Session 7 clarifications
Adds new goals and retires outdated ones
"""

from cascade_db import add_goal, retire_goal, get_all_goals
from datetime import datetime

print("\n" + "="*60)
print("Updating Project Cascade Goals (Session 7)")
print("="*60 + "\n")

# Get existing goals to see what's there
all_goals = get_all_goals()
print(f"Current goals in database: {len(all_goals)}")
for goal in all_goals:
    print(f"  - [{goal['status']}] {goal['goal_text'][:60]}...")

print("\n" + "="*60)
print("Adding New Goals from Session 7")
print("="*60 + "\n")

# New goals based on today's session
new_goals = [
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

for goal_data in new_goals:
    try:
        add_goal(
            goal_text=goal_data["text"],
            category=goal_data["category"]
        )
        print(f"✓ Added [{goal_data['category']}]: {goal_data['text'][:60]}...")
    except Exception as e:
        print(f"⚠️  Error adding goal: {e}")

print("\n" + "="*60)
print("Goal Update Complete")
print("="*60)
print("\nProject Goals now include:")
print("  • Primary: Cascade detection via autonomous monitoring")
print("  • Primary: Daily infrastructure monitoring (refined from real-time)")
print("  • Supporting: 4-routine automation pipeline")
print("  • Supporting: System documentation for continuity")
print("  • Supporting: Bifurcation point identification")
print("  • Supporting: Geographic bifurcation mapping")
print("\n")

if __name__ == '__main__':
    pass
