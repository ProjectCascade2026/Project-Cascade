#!/usr/bin/env python3
"""
Test Substack email ingestion with realistic sample emails.
Run this to see cascade signals and findings imported into the database.
"""

from cascade_db import add_signal, add_finding
from datetime import datetime, timedelta
import re

# Sample Substack emails with realistic cascade-relevant content
TEST_EMAILS = [
    {
        'author': 'Dr. Vaclav Smil',
        'subject': 'Energy Transition Reality: Why Current Semiconductor Supply Chains Cannot Support Grid Modernization',
        'body': '''
New analysis shows TSMC fab capacity constraints will limit solar inverter production through 2027.
Current global fab utilization at 94%. Taiwan produces 92% of advanced chips (5nm-7nm).

Key findings:
- Solar panel deployment requires 2.3 trillion inverter chips by 2030
- Current TSMC expansion adds only 15% capacity annually
- 3-5 year fab construction timeline creates 2025-2027 bottleneck
- Supply shock would delay grid modernization 18-24 months

This creates a bifurcation point: either accelerate distributed solar (lower energy ROI) or accept
grid modernization delays with increased blackout risk during 2026-2028 extreme weather events.
        ''',
        'date': '2026-08-15'
    },
    {
        'author': 'Prof. Simon Wardley',
        'subject': 'Cascading Fertilizer Crisis: Why Russia Sanctions Trigger Global Food System Collapse',
        'body': '''
Russia supplies 30% of global potash; Ukraine provides 7% of fertilizer nutrients globally.
Current disruptions show feedback amplification patterns:

Month 1: Russia export curtailment → potash prices +45%
Month 2: Farmers reduce application → yields drop 12-18%
Month 3: Global grain shortage → food prices +$2-4/bushel
Month 4: Developing nations cut imports → malnutrition spike

The system has only 8-9 weeks of global grain buffer. A coordinated disruption
(sanctions + climate shock + hoarding) would trigger famine conditions in Sub-Saharan Africa
and South Asia within 60 days.

Institutional response lag is 4-6 months (policy → procurement → delivery).
This is a classic coordination failure at a bifurcation point.
        ''',
        'date': '2026-08-14'
    },
    {
        'author': 'Dr. Kate Marvel',
        'subject': 'Water Scarcity Tipping Point: Himalayan Glaciers and Asian Monsoon Collapse',
        'body': '''
Latest satellite data shows Himalayan glacier mass loss accelerating to 1.2 trillion tons/year.
This feeds 2 billion people via six major Asian river systems.

Critical threshold: If glacier loss exceeds 1.5 trillion tons/year, monsoon circulation patterns bifurcate.
Current trajectory reaches this threshold in 18-24 months.

Consequences of bifurcation:
- India: 40% precipitation decline, crop failure in Punjab/Haryana
- China: Yellow/Yangtze rivers drop 30%, hydropower generation -45%
- Southeast Asia: Monsoon timing shifts 4-6 weeks, flash flooding + drought

Regional cascade: Water conflict → food shortage → migration → institutional collapse in
developing economies. Geopolitical shock probability 60% within 3 years.
        ''',
        'date': '2026-08-13'
    },
    {
        'author': 'David Korowicz',
        'subject': 'Rare Earth Supply Chain Fragility: China Controls 85% of Processing, Zero Substitutes',
        'body': '''
China refines 75-85% of global rare earth materials. New export controls effective August 2026.
Military/defense applications now constrained:

- Fighter jet engines require dysprosium (China: 95% processing)
- Satellite electronics require neodymium magnets (China: exclusive supply)
- Quantum computing requires specific lanthanides (China: 100% controlled)

Alternative refining capacity:
- USA: 0 active refineries (Molycorp closed 2015)
- Europe: 1 facility, limited scale
- Build new refinery: 5-7 years, $2-3 billion

This creates a supply chain bifurcation: Either accept Chinese processing dependency or
accept 5-7 year military technology gap. NATO cannot negotiate this away.

Cascading effect: Technology parity loss → geopolitical vulnerability → potential conflict escalation.
        ''',
        'date': '2026-08-12'
    },
    {
        'author': 'Nate Hagens',
        'subject': 'Measurement Blindness: Why Economic Models Cannot See Systemic Collapse',
        'body': '''
GDP-based economic modeling has fundamental blind spots in cascade analysis:

1. Lag time problem: GDP reports 3-month delay, but cascades operate on 2-4 week timescales
2. Aggregation problem: Regional collapse (Sub-Saharan Africa -40% GDP) masked by global +2% growth
3. Nonlinearity problem: Models assume linear relationships; cascades are exponential
4. Feedback blindness: Models don't capture positive feedback loops (supply shock → hoarding → shortage)

Real-time measurement challenges:
- Fertilizer demand data: 60-day lag (farmers report late)
- Semiconductor inventory: 45-day reporting lag from TSMC
- Food supply status: No real-time global tracking system exists
- Water levels: Satellite data available but not integrated into policy models

Policy implication: By the time we measure the problem in economic data, the cascade
is already 60-90 days advanced and potentially irreversible.

This is an institutional lag + measurement blindness combination creating systemic risk.
        ''',
        'date': '2026-08-11'
    }
]

def main():
    print("\n" + "="*60)
    print("🧪 Testing Substack Email Import Pipeline")
    print("   Sample Cascade Research Emails")
    print("="*60 + "\n")

    # Import the parse and import functions
    from import_substack_signals import parse_substack_email, import_substack_signals

    print(f"📧 Processing {len(TEST_EMAILS)} test emails...\n")

    # Import the test emails
    signal_count, finding_count = import_substack_signals(TEST_EMAILS)

    print(f"\n✅ Test Import Complete!")
    print(f"   • Signals added: {signal_count}")
    print(f"   • Findings added: {finding_count}")
    print(f"   • Total entries: {signal_count + finding_count}")
    print("\n" + "="*60)
    print("\n📊 Next Steps:")
    print("   1. Open your Streamlit app: https://project-cascade-strangelove.streamlit.app/")
    print("   2. Go to 'Research Findings' page")
    print("   3. Look for new findings from: Smil, Wardley, Marvel, Korowicz, Hagens")
    print("   4. Check 'System Dynamics' for signal distribution by node")
    print("   5. Check 'Amplitude' for node activation frequencies")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
