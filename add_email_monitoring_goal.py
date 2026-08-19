#!/usr/bin/env python3
"""
Add new goal: Monitor email insights from cascade analysts
Discovered through fresh Gmail analysis showing researcher alignment
"""

from cascade_db import add_goal, get_all_goals

print("\n" + "="*70)
print("Adding New Project Goal from Fresh Analysis")
print("="*70 + "\n")

# Check current goals
existing_goals = get_all_goals()
print("Current goals in database: " + str(len(existing_goals)))

# New goal based on Gmail analysis findings
new_goal = {
    "text": "Monitor email insights from established cascade analysts (Great Simplification, geopolitics researchers, climate scientists, economic thinkers) to surface early bifurcation warnings from domain experts",
    "category": "supporting"
}

print("\nAdding new goal:")
print("  Category: " + new_goal['category'])
print("  Text: " + new_goal['text'] + "\n")

try:
    goal_id = add_goal(
        goal_text=new_goal["text"],
        category=new_goal["category"]
    )
    print("[OK] Goal added successfully (ID: " + str(goal_id) + ")")
    
    # Verify
    updated_goals = get_all_goals()
    print("\nTotal goals now: " + str(len(updated_goals)))
    print("\nAll active goals:")
    for goal in updated_goals:
        status = goal.get('status', 'unknown')
        print("  [" + status + "] " + goal['goal_text'][:60] + "...")
    
except Exception as e:
    print("[ERROR] Error adding goal: " + str(e))

print("\n" + "="*70 + "\n")
