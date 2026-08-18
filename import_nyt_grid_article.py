#!/usr/bin/env python3
"""
Import signals from NYT article: "What if America Went Completely Dark?"
Date: August 18, 2026
Theme: Power grid vulnerability, transformer shortage, cascading infrastructure failure
"""

from cascade_db import add_signal, add_finding
from datetime import datetime

def import_nyt_grid_signals():
    """Extract cascade signals from NYT grid infrastructure article"""

    signals = [
        # Transformer Shortage & Supply Chain (Node 7: Economic Depletion, Node 4: Rate of Change)
        {
            'node': 7,
            'domain': 'Energy Infrastructure',
            'description': 'Transformer lead times increased from <1 year to 128 weeks (2.5 years) post-pandemic',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 7,
            'domain': 'Supply Chain',
            'description': 'Only 1 U.S. mill produces grain-oriented electrical steel (GOES) needed for transformers',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 4,
            'domain': 'Demand Acceleration',
            'description': 'Transformer demand expected to double from 2025 to 2027 due to data center expansion',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 4,
            'domain': 'AI Electricity Demand',
            'description': 'LLM training consumes 500+ MW; switching modes creates load whipsawing',
            'severity': 'serious',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        # Infrastructure Age & Vulnerability (Node 8: Infrastructure Brittleness)
        {
            'node': 8,
            'domain': 'Infrastructure Age',
            'description': '75% of distribution transformers past 50-year service life expectancy',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 8,
            'domain': 'Large Transformer Age',
            'description': 'Average age of large power transformers estimated at 38-40 years (12 years ago)',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        # Physical Security Threats (Node 3: Institutional Suppression, Node 10: Coordination Cascade)
        {
            'node': 3,
            'domain': 'Physical Security',
            'description': 'Metcalf substation attack (2013): 17 transformers disabled by 2 trained shooters in 20 minutes',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 3,
            'domain': 'System Vulnerability',
            'description': 'FERC analysis: 9 critical substations knocked out could black out entire U.S.',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 10,
            'domain': 'Cascading Failure',
            'description': 'Long-term blackout would cascade: water treatment → fuel delivery → food → social breakdown within days',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        # Recent Attacks (Node 3: Institutional Suppression)
        {
            'node': 3,
            'domain': 'Infrastructure Attack',
            'description': 'Moore County NC (Dec 2022): Transformers disabled; 45,000 lost power for up to 5 days',
            'severity': 'serious',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 3,
            'domain': 'Extremist Threat',
            'description': '2024: Five white supremacist group members sentenced for plotting to destroy transformers',
            'severity': 'serious',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        # State Actor Threats (Node 10: Coordination Cascade)
        {
            'node': 10,
            'domain': 'Cyber/Physical Threat',
            'description': 'China caught installing software backdoor in transformer shipped to U.S. federal utility',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 10,
            'domain': 'Geopolitical Risk',
            'description': 'Iran linked to water system sabotage; grid vulnerable as attack surface for state actors',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        # Workforce & Manufacturing (Node 6: Measurement Capacity, Node 7: Economic Depletion)
        {
            'node': 6,
            'domain': 'Manufacturing Visibility',
            'description': 'Transformer manufacturing highly skilled/bespoke; Central Moloney has 11,000+ unique designs',
            'severity': 'serious',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 7,
            'domain': 'Labor Shortage',
            'description': 'Severe shortage of master craftsmen; basic skills lacking across transformer industry',
            'severity': 'serious',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        # Resilience Challenges (Node 12: Adaptation Exhaustion)
        {
            'node': 12,
            'domain': 'Emergency Response',
            'description': 'No comprehensive national plan for multi-year blackout response; GridEx is voluntary participation',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 12,
            'domain': 'Recovery Infrastructure',
            'description': 'Replacement of 180 transformers could take years; only handful of Schnabel rail cars in North America',
            'severity': 'critical',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        # Solutions & Emerging Technologies (Node 4: Rate of Change)
        {
            'node': 4,
            'domain': 'Innovation Pipeline',
            'description': 'Solid-state transformers show promise but still 5-10 years from large-scale deployment',
            'severity': 'warning',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
        {
            'node': 4,
            'domain': 'Grid Resilience',
            'description': 'Battery storage expected to double 2025-2027; distributed backup power reduces cascade risk',
            'severity': 'warning',
            'date': '2026-08-18',
            'source': 'NYT Magazine: National Blackout'
        },
    ]

    count = 0
    for signal in signals:
        try:
            add_signal(
                signal['node'],
                signal['domain'],
                signal['description'],
                signal['severity'],
                signal['date'],
                signal['source']
            )
            count += 1
        except Exception as e:
            print(f"⚠ Error adding signal: {e}")

    return count

def import_nyt_grid_findings():
    """Extract research findings organized by mechanism"""

    findings = [
        {
            'mechanism': 'Threshold Dynamics',
            'text': 'Transformer lead times crossed critical threshold: 128 weeks means replacement impossible during cascading failures',
            'confidence': 0.92,
            'evidence': 'Siemens Energy, NERC data; prepandemic <1 year → current 128 weeks'
        },
        {
            'mechanism': 'Institutional Lag',
            'text': 'Defense Production Act invoked 2022 and 2026 with minimal effect; factory timelines remain unmoved by policy',
            'confidence': 0.85,
            'evidence': 'Biden 2022 DPA vs Trump 2026 DPA; no new mills opened'
        },
        {
            'mechanism': 'Feedback Amplification',
            'text': 'Supply chain panic-buying created self-fulfilling prophecy: utilities seeing longer lead times ordered more transformers, further extending delivery',
            'confidence': 0.88,
            'evidence': 'Tim Holt (Siemens): pandemic → longer delivery → panic-buying → longer delivery'
        },
        {
            'mechanism': 'Coupling & Interdependence',
            'text': '9 strategically targeted substations can collapse entire U.S. grid; system designed for redundancy lacks resilience',
            'confidence': 0.91,
            'evidence': 'FERC power flow analysis; vulnerability confirmed at Metcalf attack'
        },
        {
            'mechanism': 'Infrastructure Built for Still Climate',
            'text': 'Transformers designed for historical load patterns; AI data centers create 500MW+ spikes switching modes instantaneously',
            'confidence': 0.89,
            'evidence': 'Brian Dow (Amperesand): LLM training load whipsawing; grid not equipped for this'
        },
        {
            'mechanism': 'Measurement & Uncertainty',
            'text': 'No comprehensive inventory of transformer age/condition; 55,000 substations across country with uneven security',
            'confidence': 0.87,
            'evidence': 'DHS tour 2013 found awareness of vulnerability but no national plan'
        },
        {
            'mechanism': 'Economic Depletion',
            'text': 'Transformer replacement cost approaching Fabergé egg economics: $14M each; 180-unit cascade failure costs $2.5B+ before shipping/installation',
            'confidence': 0.90,
            'evidence': 'Central Moloney, Siemens; massive capital requirements for grid hardening'
        },
        {
            'mechanism': 'Tipping Points & Bifurcation',
            'text': 'Transformer production capacity at inflection point: demand will double 2025-2027; supply cannot scale in time',
            'confidence': 0.93,
            'evidence': 'Manufacturing expansion underway but factories take 3-5 years to build'
        },
    ]

    count = 0
    for finding in findings:
        try:
            add_finding(
                finding['mechanism'],
                finding['text'],
                finding['confidence'],
                supporting_evidence=finding['evidence'],
                status='active'
            )
            count += 1
        except Exception as e:
            print(f"⚠ Error adding finding: {e}")

    return count

def main():
    print("\n" + "="*60)
    print("📰 Importing NYT Grid Article Signals")
    print("   'What if America Went Completely Dark?' - Aug 18, 2026")
    print("="*60 + "\n")

    signal_count = import_nyt_grid_signals()
    finding_count = import_nyt_grid_findings()

    print(f"\n✅ Import complete!")
    print(f"   • Signals added: {signal_count}")
    print(f"   • Findings added: {finding_count}")
    print(f"   • Total cascade impact entries: {signal_count + finding_count}")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
