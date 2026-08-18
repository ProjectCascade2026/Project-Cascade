import sqlite3

conn = sqlite3.connect('cascade_data.db')
c = conn.cursor()

print("\n" + "="*60)
print("🔍 CASCADE NODE STATUS CHECK")
print("="*60 + "\n")

result = c.execute('SELECT node_id, name, status FROM cascade_nodes ORDER BY node_id').fetchall()
for node_id, name, status in result:
    print(f"Node {node_id}: {name}")
    print(f"  └─ Status: {status}")

conn.close()
