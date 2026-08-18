#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('cascade_data.db')
c = conn.cursor()

print("\n" + "="*60)
print("📊 CASCADE DATABASE DIAGNOSTICS")
print("="*60 + "\n")

# Count orphaned vs assigned
orphaned = c.execute('SELECT COUNT(*) FROM signals WHERE node_id IS NULL').fetchone()[0]
assigned = c.execute('SELECT COUNT(*) FROM signals WHERE node_id IS NOT NULL').fetchone()[0]

print(f"Orphaned signals (NULL node_id): {orphaned}")
print(f"Assigned signals: {assigned}")
print(f"Total signals: {orphaned + assigned}\n")

# Distribution by node
print("Signals per node:")
nodes = c.execute('SELECT node_id, COUNT(*) as cnt FROM signals WHERE node_id IS NOT NULL GROUP BY node_id ORDER BY node_id').fetchall()
for node_id, count in nodes:
    print(f"  Node {node_id}: {count} signals")

# Sample orphaned signals
print(f"\nFirst 5 orphaned signals:")
orphaned_samples = c.execute('SELECT signal_id, timestamp, description FROM signals WHERE node_id IS NULL LIMIT 5').fetchall()
for sig_id, ts, desc in orphaned_samples:
    print(f"  ID {sig_id} ({ts}): {desc[:50]}...")

conn.close()
print("\n" + "="*60 + "\n")
