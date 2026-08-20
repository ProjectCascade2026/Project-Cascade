#!/usr/bin/env python3
"""
Add infrastructure defense research findings to cascade database
Based on Economist research: "Why the world's richest country can't defend vital infrastructure"
Critical bifurcation: speed mismatch between threat evolution and institutional response
"""

import sys
import os

# Add cascade_app_package to path for imports
cascade_path = os.path.expanduser("~/cascade_app_package")
sys.path.insert(0, cascade_path)

try:
    from cascade_db import add_signal, add_finding
except ImportError as e:
    print(f"ERROR: Could not import cascade_db: {e}")
    print(f"Make sure cascade_db.py is in {cascade_path}")
    sys.exit(1)

print("\n" + "="*60)
print("Adding Infrastructure Defense Research Findings")
print("="*60 + "\n")

# Define research-based signals and findings
signals_to_add = [
    {
        'node': 4,  # Rate of Change - threat evolution faster than institutional response
        'domain': 'Threat Evolution Speed vs Response Time',
        'description': 'Critical bifurcation identified: cybersecurity threats escalate in hours, patches deploy in months, policy responds in years',
        'severity': 'critical',
        'date': '2026-08-20',
        'source': 'Economist: Why world\'s richest country can\'t defend vital infrastructure'
    },
    {
        'node': 6,  # Measurement Capacity Erosion
        'domain': 'Cybersecurity Threat Monitoring',
        'description': '60 new vulnerabilities discovered daily; infrastructure monitoring systems cannot keep pace with threat generation rate',
        'severity': 'critical',
        'date': '2026-08-20',
        'source': 'Infrastructure defense research - vulnerability discovery rate'
    },
    {
        'node': 8,  # Infrastructure Brittleness
        'domain': 'Water Utility Cybersecurity Gaps',
        'description': '90% of small water utilities lack dedicated cybersecurity teams; creates cascading vulnerability across food/water supply systems',
        'severity': 'critical',
        'date': '2026-08-20',
        'source': 'Infrastructure defense research - water system resilience'
    },
    {
        'node': 12,  # Adaptation Exhaustion
        'domain': 'Institutional Response Capacity Exhaustion',
        'description': '75% year-over-year increase in cybersecurity attacks; institutional response mechanisms approaching saturation',
        'severity': 'critical',
        'date': '2026-08-20',
        'source': 'Economist research - attack frequency escalation'
    }
]

findings_to_add = [
    {
        'mechanism': 'Speed Mismatch Bifurcation',
        'text': 'Research from Economist identifies critical bifurcation point: threats escalate hourly, patches deploy monthly, policy responds yearly. This speed mismatch creates permanent window of vulnerability. Evidence: 75% YoY attack increase; 60 new vulnerabilities/day; 90% of small water utilities lack cybersecurity teams. Maps to cascade nodes: Node 4 (Rate Change), Node 6 (Measurement), Node 8 (Brittleness), Node 12 (Adaptation Exhaustion).',
        'confidence': 0.92,
        'evidence': 'Economist investigation into US infrastructure defense gaps; cross-mapped to Project Cascade node theory'
    },
    {
        'mechanism': 'Water System Cascade Vulnerability',
        'text': 'Small water utilities (90% of systems) lack dedicated cybersecurity teams, creating systemic cascade risk. Compromised water system triggers food supply disruption, population displacement, economic cascade. Critical gap in last-mile infrastructure defense.',
        'confidence': 0.88,
        'evidence': 'Infrastructure defense research; maps to Node 3 (Water System), Node 5 (Food System), Node 7 (Economic/Supply Chain)'
    },
    {
        'mechanism': 'Institutional Response Saturation',
        'text': 'Attack frequency (75% YoY increase) exceeding institutional capacity to respond. Vulnerability discovery rate (60/day) exceeding patch deployment rate. System approaching adaptation exhaustion - inability to respond to new threats in real-time.',
        'confidence': 0.85,
        'evidence': 'Cybersecurity trend analysis; maps to Node 12 (Adaptation Exhaustion), Node 8 (Brittleness)'
    }
]

# Add signals
print("Adding signals from infrastructure defense research...\n")
signal_count = 0

for signal in signals_to_add:
    try:
        add_signal(
            node_id=signal['node'],
            domain=signal['domain'],
            description=signal['description'],
            severity=signal['severity'],
            date_recorded=signal['date'],
            source=signal['source']
        )
        print(f"[OK] Signal added: Node {signal['node']} - {signal['domain']}")
        signal_count += 1
    except Exception as e:
        print(f"[ERROR] Failed to add signal: {e}")

# Add findings
print(f"\nAdding findings ({len(findings_to_add)} total)...\n")
finding_count = 0

for finding in findings_to_add:
    try:
        add_finding(
            mechanism=finding['mechanism'],
            finding_text=finding['text'],
            confidence_level=finding['confidence'],
            supporting_evidence=finding['evidence']
        )
        print(f"[OK] Finding added: {finding['mechanism']}")
        finding_count += 1
    except Exception as e:
        print(f"[ERROR] Failed to add finding: {e}")

print("\n" + "="*60)
print("Infrastructure Defense Research Integration Complete")
print("="*60)
print(f"\nSignals added: {signal_count}")
print(f"Findings added: {finding_count}")
print(f"Total additions: {signal_count + finding_count}")
print("\nFocus areas added:")
print("  - Node 4: Rate of Change (threat escalation)")
print("  - Node 6: Measurement Capacity Erosion")
print("  - Node 8: Infrastructure Brittleness (water utilities)")
print("  - Node 12: Adaptation Exhaustion (institutional saturation)")
print()
