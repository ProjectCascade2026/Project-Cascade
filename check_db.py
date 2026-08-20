import sqlite3
conn = sqlite3.connect('cascade_data.db')
c = conn.cursor()
signals = c.execute('SELECT COUNT(*) FROM signals').fetchone()[0]
findings = c.execute('SELECT COUNT(*) FROM research_findings').fetchone()[0]
sequences = c.execute('SELECT COUNT(*) FROM cascade_sequences').fetchone()[0]
nodes = c.execute('SELECT COUNT(*) FROM cascade_nodes').fetchone()[0]
print(f'Signals: {signals}')
print(f'Findings: {findings}')
print(f'Sequences: {sequences}')
print(f'Nodes: {nodes}')
conn.close()
