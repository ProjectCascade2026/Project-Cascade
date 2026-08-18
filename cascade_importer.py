# -*- coding: utf-8 -*-
"""
Data Importer - Parse existing markdown files and populate cascade_db
"""

import re
import json
from datetime import datetime
from pathlib import Path
import sqlite3
from cascade_db import init_db, get_connection

CONFLUENCE_DIR = Path(__file__).parent

# Node definitions (13 nodes from Project Cascade)
NODES = {
    1: ("Water Bankruptcy", "Water system transition to scarcity-based management"),
    2: ("Regulatory Capture", "Exemptions retained rather than removed"),
    3: ("Institutional Suppression", "Change rejection via automatic denial mechanisms"),
    4: ("Rate of Change", "System change accelerating beyond adaptive capacity"),
    5: ("Thresholds Becoming Floors", "Disasters establish new lower baselines"),
    6: ("Measurement Capacity Erosion", "Inability to see/measure system degradation"),
    7: ("Economic Depletion", "Capital exhaustion from continuous crisis response"),
    8: ("Infrastructure Brittleness", "Built for stable climate, fails under change"),
    9: ("Scenario Planning Collapse", "Models only return 'solvable' pathways"),
    10: ("Coordination Cascade Failure", "System interdependencies amplify collapse"),
    11: ("Infrastructure Built for Still Climate", "Designed for historical conditions"),
    12: ("Adaptation Exhaustion", "Continuous change exhausts adaptive capacity"),
    13: ("Change/Adaptation Lag", "Systems optimize for past, not future"),
}

def import_cascade_nodes():
    """Initialize cascade nodes"""
    conn = get_connection()
    c = conn.cursor()

    for node_id, (name, mechanism) in NODES.items():
        c.execute('''INSERT OR IGNORE INTO cascade_nodes (node_id, name, mechanism, status)
                     VALUES (?, ?, ?, ?)''',
                  (node_id, name, mechanism, 'monitoring'))

    conn.commit()
    conn.close()
    print(f"✓ Imported {len(NODES)} cascade nodes")

def import_from_confluence_state():
    """Parse confluence_state.md for reference points and system state"""
    state_file = CONFLUENCE_DIR / 'confluence_state.md'

    if not state_file.exists():
        print("⚠ confluence_state.md not found")
        return

    content = state_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    # Extract reference points (look for patterns like "Amplitude 34" or "Frequency 44")
    ref_patterns = {
        'Amplitude': r'Amplitude[:\s]+(\d+)',
        'Frequency': r'Frequency[:\s]+(\d+)',
        'Interconnectedness': r'Interconnectedness[:\s]+(\d+)',
        'Systematic Underestimation': r'Systematic Underestimation[:\s]+(\d+)',
    }

    for metric, pattern in ref_patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            value = float(matches[-1])  # Take the most recent value
            c.execute('''INSERT INTO reference_points (metric_name, value, category)
                         VALUES (?, ?, ?)''',
                      (metric, value, 'cascade_state'))

    conn.commit()
    conn.close()
    print("✓ Imported reference points from confluence_state.md")

def import_cascade_sequences():
    """Parse CASCADING_NODES_WATCH_LOG.md for CASCADE sequences"""
    watch_file = CONFLUENCE_DIR / 'CASCADING_NODES_WATCH_LOG.md'

    if not watch_file.exists():
        print("⚠ CASCADING_NODES_WATCH_LOG.md not found")
        return

    content = watch_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    # Parse CASCADE entries (CASCADE 1-12)
    cascade_pattern = r'\*\*CASCADE (\d+)[:\s]+.*?\(Node (\d+).*?→.*?Node (\d+)'
    cascades = re.findall(cascade_pattern, content, re.IGNORECASE)

    for cascade_num, node_a, node_b in cascades:
        cascade_id = int(cascade_num)
        node_sequence = f"{node_a}->{node_b}"

        # Extract confidence if available
        confidence_pattern = rf'CASCADE {cascade_num}.*?(?:confidence|confidence.*?|Confidence:.*?)(\d+)'
        conf_match = re.search(confidence_pattern, content, re.IGNORECASE | re.DOTALL)
        confidence = float(conf_match.group(1)) / 100 if conf_match else 0.75

        c.execute('''INSERT OR IGNORE INTO cascade_sequences
                     (cascade_id, name, node_sequence, confidence)
                     VALUES (?, ?, ?, ?)''',
                  (cascade_id, f"CASCADE {cascade_id}", node_sequence, confidence))

    conn.commit()
    conn.close()
    print(f"✓ Imported {len(cascades)} CASCADE sequences")

def import_baseline_failures():
    """Parse BASELINE_RETURN_FAILURE_RESEARCH_20260818.md"""
    baseline_file = CONFLUENCE_DIR / 'BASELINE_RETURN_FAILURE_RESEARCH_20260818.md'

    if not baseline_file.exists():
        print("⚠ Baseline failure research file not found")
        return

    content = baseline_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    # Extract baseline shifts (look for patterns like "Colorado River -33%")
    baseline_pattern = r'([A-Za-z\s]+)\s+(-?\d+)%'
    failures = re.findall(baseline_pattern, content)

    for location_or_sector, shift in failures[:20]:  # Limit to prevent duplicates
        location_or_sector = location_or_sector.strip()
        if location_or_sector and len(location_or_sector) > 3:
            c.execute('''INSERT INTO baseline_failures (geography, sector, mechanism, baseline_shift_percent)
                         VALUES (?, ?, ?, ?)''',
                      (location_or_sector, 'mixed', 'baseline_return_failure', float(shift)))

    conn.commit()
    conn.close()
    print(f"✓ Imported baseline return failure data")

def import_signals_from_confluence():
    """Extract all signals from confluence_state.md and other markdown files"""
    confluence_file = CONFLUENCE_DIR / 'confluence_state.md'

    if not confluence_file.exists():
        print("⚠ confluence_state.md not found")
        return

    content = confluence_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    signal_count = 0

    # Pattern 1: Extract from node entries like "**Node 4 (Rate of Change...) — STRONG ACTIVE SIGNAL**"
    # Each node section contains multiple bullet-pointed instances
    node_pattern = r'\*\*Node (\d+).*?(STRONG ACTIVE|MODERATE|MINIMAL|EMERGING|NO).*?SIGNAL\*\*'

    # Find all node sections - split by nodes
    lines = content.split('\n')
    node_sections = {}  # Map node_id -> section text

    current_node = None
    current_section = []

    for line in lines:
        node_match = re.match(r'\*\*Node (\d+)', line)
        if node_match:
            # Save previous node section
            if current_node is not None:
                node_sections[current_node] = '\n'.join(current_section)

            current_node = int(node_match.group(1))
            current_section = [line]
        elif current_node is not None:
            # Check if this is a new section (starts with ##)
            if line.startswith('##') and not line.startswith('###'):
                # End of node sections
                if current_node is not None:
                    node_sections[current_node] = '\n'.join(current_section)
                current_node = None
                current_section = []
            else:
                current_section.append(line)

    # Add last node if any
    if current_node is not None:
        node_sections[current_node] = '\n'.join(current_section)

    for node_id, section in node_sections.items():
        # Extract signal status
        status_match = re.search(r'(STRONG ACTIVE|MODERATE|MINIMAL|EMERGING|NO) (?:ACTIVE )?SIGNAL', section, re.IGNORECASE)
        if not status_match:
            continue

        status_text = status_match.group(1).upper()

        # Map status to severity
        severity_map = {
            'STRONG ACTIVE': 'critical',
            'MODERATE': 'serious',
            'EMERGING': 'warning',
            'MINIMAL': 'warning',
            'NO': 'info'
        }
        severity = severity_map.get(status_text, 'warning')

        # Extract bullet points (instances) from this section
        bullet_pattern = r'^\s*[-•]\s+(.+?)$'
        bullets = re.findall(bullet_pattern, section, re.MULTILINE)

        for instance_text in bullets:
            # Clean up the instance text
            instance_text = instance_text.strip()
            if not instance_text or len(instance_text) < 10:
                continue

            # Try to extract domain from the instance text or use generic "cascade"
            domain = 'cascade'
            if any(word in instance_text.lower() for word in ['climate', 'weather', 'ice', 'temperature']):
                domain = 'climate'
            elif any(word in instance_text.lower() for word in ['water', 'river', 'lake', 'groundwater']):
                domain = 'water'
            elif any(word in instance_text.lower() for word in ['agriculture', 'crop', 'farm', 'food']):
                domain = 'agriculture'
            elif any(word in instance_text.lower() for word in ['institutional', 'governance', 'policy']):
                domain = 'governance'
            elif any(word in instance_text.lower() for word in ['economic', 'funding', 'finance', 'cost']):
                domain = 'economics'
            elif any(word in instance_text.lower() for word in ['species', 'ecosystem', 'biodiversity', 'wildlife']):
                domain = 'ecology'
            elif any(word in instance_text.lower() for word in ['health', 'disease', 'medical']):
                domain = 'health'

            # Truncate long descriptions
            description = instance_text[:500] if len(instance_text) > 500 else instance_text

            try:
                c.execute('''INSERT INTO signals
                            (node_id, domain, description, severity, date_recorded, source, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (node_id, domain, description, severity, datetime.now().isoformat(),
                          'confluence_state.md', 'active'))
                signal_count += 1
            except Exception as e:
                print(f"⚠ Error inserting signal for Node {node_id}: {e}")

    conn.commit()
    conn.close()
    print(f"✓ Imported {signal_count} signals from confluence_state.md")
    return signal_count


def import_signals_from_daily_findings():
    """Extract signals from daily_findings.md"""
    findings_file = CONFLUENCE_DIR / 'daily_findings.md'

    if not findings_file.exists():
        return 0

    content = findings_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    signal_count = 0

    # Extract findings section
    findings_pattern = r'##\s+Findings\s*\n(.*?)(?=##|$)'
    findings_match = re.search(findings_pattern, content, re.DOTALL)

    if not findings_match:
        conn.close()
        return 0

    findings_section = findings_match.group(1)

    # Extract bullet points
    bullets = re.findall(r'^\s*[-•]\s+(.+?)$', findings_section, re.MULTILINE)

    for finding_text in bullets:
        finding_text = finding_text.strip()
        if not finding_text or len(finding_text) < 10:
            continue

        # Extract node references from finding text (e.g., "Node 4", "Nodes 7→6→11")
        node_refs = re.findall(r'Node[s]?\s*(\d+)', finding_text)

        if node_refs:
            # Use the first referenced node
            node_id = int(node_refs[0])
            domain = 'research'
            severity = 'serious'
            description = finding_text[:500]

            try:
                c.execute('''INSERT INTO signals
                            (node_id, domain, description, severity, date_recorded, source, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (node_id, domain, description, severity, datetime.now().isoformat(),
                          'daily_findings.md', 'active'))
                signal_count += 1
            except Exception as e:
                pass

    conn.commit()
    conn.close()
    return signal_count


def import_signals_from_cascading_nodes_log():
    """Extract verified CASCADE instances from CASCADING_NODES_WATCH_LOG.md"""
    log_file = CONFLUENCE_DIR / 'CASCADING_NODES_WATCH_LOG.md'

    if not log_file.exists():
        return 0

    content = log_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    signal_count = 0

    # Look for verified CASCADE sections
    # Each verified cascade mentions specific nodes
    section_pattern = r'^\*\*CASCADE (\d+):[^*]+\*\*(.*?)(?=^##|\Z)'
    matches = re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        cascade_num = match.group(1)
        cascade_section = match.group(2)

        # Extract node numbers mentioned
        node_refs = re.findall(r'Node (\d+)', cascade_section)
        unique_nodes = set(int(n) for n in node_refs)

        # Extract instances/findings from this cascade
        bullets = re.findall(r'^\s*[-•]\s+(.+?)$', cascade_section, re.MULTILINE)

        for finding_text in bullets[:5]:  # Limit findings per cascade
            finding_text = finding_text.strip()
            if not finding_text or len(finding_text) < 10:
                continue

            # Use first node if multiple mentioned
            if unique_nodes:
                node_id = min(unique_nodes)
                description = f"CASCADE {cascade_num}: {finding_text}"[:500]
                severity = 'serious'
                domain = 'cascade'

                try:
                    c.execute('''INSERT INTO signals
                                (node_id, domain, description, severity, date_recorded, source, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                             (node_id, domain, description, severity, datetime.now().isoformat(),
                              f'CASCADING_NODES_WATCH_LOG.md (CASCADE {cascade_num})', 'active'))
                    signal_count += 1
                except Exception as e:
                    pass

    conn.commit()
    conn.close()
    return signal_count


def import_signals_from_dan_evidence():
    """Extract distributed adaptation network evidence as signals"""
    dan_file = CONFLUENCE_DIR / 'DAN_CASCADE_MECHANISM_EVIDENCE_20260818.md'

    if not dan_file.exists():
        return 0

    content = dan_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    signal_count = 0

    # Extract node sections from DAN analysis
    # Pattern: ### Node N Activation or ### Node N or similar
    node_pattern = r'^###\s+Node (\d+)'
    lines = content.split('\n')
    current_node = None
    current_section = []

    for line in lines:
        node_match = re.match(node_pattern, line)
        if node_match:
            if current_node is not None and current_section:
                # Process previous node
                section_text = '\n'.join(current_section)
                # Extract both bullet points and regular text
                bullets = re.findall(r'^\s*[-•]\s+(.+?)$', section_text, re.MULTILINE)
                # Also get any quoted interpretations
                quoted = re.findall(r'\*\*Cascade Interpretation\*\*:(.+?)(?=\n\*\*|\n###|\Z)', section_text, re.DOTALL)

                all_findings = bullets + [q.strip() for q in quoted if q.strip()]

                for finding in all_findings:
                    finding = finding.strip()
                    if finding and len(finding) > 10:
                        try:
                            c.execute('''INSERT INTO signals
                                        (node_id, domain, description, severity, date_recorded, source, status)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                     (current_node, 'dan_analysis', finding[:500], 'serious',
                                      datetime.now().isoformat(), 'DAN_CASCADE_MECHANISM_EVIDENCE.md', 'active'))
                            signal_count += 1
                        except Exception as e:
                            pass

            current_node = int(node_match.group(1))
            current_section = [line]
        elif current_node is not None:
            current_section.append(line)

    # Process last node
    if current_node is not None and current_section:
        section_text = '\n'.join(current_section)
        bullets = re.findall(r'^\s*[-•]\s+(.+?)$', section_text, re.MULTILINE)
        quoted = re.findall(r'\*\*Cascade Interpretation\*\*:(.+?)(?=\n\*\*|\n###|\Z)', section_text, re.DOTALL)

        all_findings = bullets + [q.strip() for q in quoted if q.strip()]

        for finding in all_findings:
            finding = finding.strip()
            if finding and len(finding) > 10:
                try:
                    c.execute('''INSERT INTO signals
                                (node_id, domain, description, severity, date_recorded, source, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                             (current_node, 'dan_analysis', finding[:500], 'serious',
                              datetime.now().isoformat(), 'DAN_CASCADE_MECHANISM_EVIDENCE.md', 'active'))
                    signal_count += 1
                except Exception as e:
                    pass

    conn.commit()
    conn.close()
    return signal_count


def import_signals_from_new_index():
    """Parse new_index.html for signals (if accessible)"""
    # This would need HTML parsing - defer for now
    pass

def import_amplitude_watch():
    """Parse AMPLITUDE_WATCH_LOG.md for mechanism escalation tracking"""
    amp_file = CONFLUENCE_DIR / 'AMPLITUDE_WATCH_LOG.md'

    if not amp_file.exists():
        print("⚠ AMPLITUDE_WATCH_LOG.md not found")
        return 0

    content = amp_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    watch_count = 0

    # Split by node sections (### Node N: ...)
    node_pattern = r'^###\s+Node (\d+):\s+([^\n]+)'
    lines = content.split('\n')

    current_node = None
    current_node_name = None
    current_section = []

    for line in lines:
        node_match = re.match(node_pattern, line)
        if node_match:
            # Process previous node if exists
            if current_node is not None and current_section:
                section_text = '\n'.join(current_section)

                # Extract fields using regex (handle markdown bold formatting)
                current_amp_match = re.search(r'\*\*Current Amplitude\*\*[:\s]+(\d+(?:\.\d+)?)', section_text)
                prev_amp_match = re.search(r'\*\*Previous Amplitude\*\*[:\s]+(\d+(?:\.\d+)?)', section_text)
                esc_rate_match = re.search(r'\*\*Escalation Rate\*\*[:\s]+([^\n]+)', section_text)
                conf_match = re.search(r'\*\*Confidence\*\*[:\s]+([^\n]+)', section_text)
                risk_match = re.search(r'\*\*Risk Threshold\*\*[:\s]+(\d+(?:\.\d+)?)', section_text)
                meas_match = re.search(r'\*\*Measurement Basis\*\*[:\s]+([^\n]+)', section_text)
                break_match = re.search(r'\*\*Breakpoint\*\*[:\s]+([^\n]+)', section_text)
                evid_match = re.search(r'\*\*Evidence\*\*[:\s]+([^\n]+)', section_text)
                status_match = re.search(r'Amplification Status[:\s]+([A-Z_]+)', section_text)

                current_amp = float(current_amp_match.group(1)) if current_amp_match else 0
                prev_amp = float(prev_amp_match.group(1)) if prev_amp_match else 0
                esc_rate = esc_rate_match.group(1).strip() if esc_rate_match else ''
                confidence = conf_match.group(1).strip() if conf_match else 'UNKNOWN'
                risk_threshold = float(risk_match.group(1)) if risk_match else 0
                measurement = meas_match.group(1).strip() if meas_match else ''
                breakpoint = break_match.group(1).strip() if break_match else ''
                evidence = evid_match.group(1).strip() if evid_match else ''
                status = status_match.group(1) if status_match else 'MONITORING'

                try:
                    c.execute('''INSERT OR REPLACE INTO amplitude_watch
                                (node_id, node_name, current_amplitude, previous_amplitude, escalation_rate,
                                 confidence, risk_threshold, measurement_basis, breakpoint, evidence, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (current_node, current_node_name, current_amp, prev_amp, esc_rate,
                              confidence, risk_threshold, measurement, breakpoint, evidence, status))
                    watch_count += 1
                except Exception as e:
                    print(f"⚠ Error importing Node {current_node} amplitude watch: {e}")

            # Start new node section
            current_node = int(node_match.group(1))
            current_node_name = node_match.group(2).strip()
            current_section = [line]
        elif current_node is not None:
            current_section.append(line)

    # Process last node
    if current_node is not None and current_section:
        section_text = '\n'.join(current_section)

        current_amp_match = re.search(r'\*\*Current Amplitude\*\*[:\s]+(\d+(?:\.\d+)?)', section_text)
        prev_amp_match = re.search(r'\*\*Previous Amplitude\*\*[:\s]+(\d+(?:\.\d+)?)', section_text)
        esc_rate_match = re.search(r'\*\*Escalation Rate\*\*[:\s]+([^\n]+)', section_text)
        conf_match = re.search(r'\*\*Confidence\*\*[:\s]+([^\n]+)', section_text)
        risk_match = re.search(r'\*\*Risk Threshold\*\*[:\s]+(\d+(?:\.\d+)?)', section_text)
        meas_match = re.search(r'\*\*Measurement Basis\*\*[:\s]+([^\n]+)', section_text)
        break_match = re.search(r'\*\*Breakpoint\*\*[:\s]+([^\n]+)', section_text)
        evid_match = re.search(r'\*\*Evidence\*\*[:\s]+([^\n]+)', section_text)
        status_match = re.search(r'Amplification Status[:\s]+([A-Z_]+)', section_text)

        current_amp = float(current_amp_match.group(1)) if current_amp_match else 0
        prev_amp = float(prev_amp_match.group(1)) if prev_amp_match else 0
        esc_rate = esc_rate_match.group(1).strip() if esc_rate_match else ''
        confidence = conf_match.group(1).strip() if conf_match else 'UNKNOWN'
        risk_threshold = float(risk_match.group(1)) if risk_match else 0
        measurement = meas_match.group(1).strip() if meas_match else ''
        breakpoint = break_match.group(1).strip() if break_match else ''
        evidence = evid_match.group(1).strip() if evid_match else ''
        status = status_match.group(1) if status_match else 'MONITORING'

        try:
            c.execute('''INSERT OR REPLACE INTO amplitude_watch
                        (node_id, node_name, current_amplitude, previous_amplitude, escalation_rate,
                         confidence, risk_threshold, measurement_basis, breakpoint, evidence, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (current_node, current_node_name, current_amp, prev_amp, esc_rate,
                      confidence, risk_threshold, measurement, breakpoint, evidence, status))
            watch_count += 1
        except Exception as e:
            print(f"⚠ Error importing Node {current_node} amplitude watch: {e}")

    conn.commit()
    conn.close()
    print(f"✓ Imported {watch_count} amplitude watch entries")
    return watch_count


def import_daily_findings():
    """Parse daily_findings.md for today's entries"""
    findings_file = CONFLUENCE_DIR / 'daily_findings.md'

    if not findings_file.exists():
        return

    content = findings_file.read_text(encoding='utf-8')
    conn = get_connection()
    c = conn.cursor()

    # Parse date from first heading: # Daily Findings — YYYY-MM-DD
    date_pattern = r'# Daily Findings[—\s]+(\d{4}-\d{2}-\d{2})'
    date_match = re.search(date_pattern, content)

    if not date_match:
        conn.close()
        return

    date_str = date_match.group(1)

    # Parse sections
    def extract_section(section_name):
        """Extract bullet points from a section"""
        pattern = rf'##\s+{section_name}\s*\n(.*?)(?=##|$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section_content = match.group(1)
            # Extract bullet points
            bullets = re.findall(r'^\s*[-•]\s+(.+)$', section_content, re.MULTILINE)
            return bullets
        return []

    overview_pattern = r'##\s+Overview\s*\n(.*?)(?=##)'
    overview_match = re.search(overview_pattern, content, re.DOTALL)
    overview = overview_match.group(1).strip() if overview_match else ""

    findings = extract_section('Findings')
    methodological = extract_section('Methodological Insights')
    theoretical = extract_section('Theoretical Model Advances')

    # Convert to JSON strings for storage
    findings_json = json.dumps(findings)
    methodological_json = json.dumps(methodological)
    theoretical_json = json.dumps(theoretical)

    # Add or update entry
    try:
        c.execute('DELETE FROM daily_findings WHERE date = ?', (date_str,))
        c.execute('''INSERT INTO daily_findings
                     (date, overview, findings, methodological_insights, theoretical_advances)
                     VALUES (?, ?, ?, ?, ?)''',
                  (date_str, overview, findings_json, methodological_json, theoretical_json))
        conn.commit()
        print(f"✓ Imported daily findings for {date_str}")
    except Exception as e:
        print(f"⚠ Error importing daily findings: {e}")
    finally:
        conn.close()

def import_systematic_underestimations():
    """Populate comprehensive systematic underestimation findings"""
    from cascade_db import add_underestimation

    findings = [
        # Climate Models - 4 findings
        {
            'domain': 'Climate Models',
            'category': 'Warming Speed',
            'finding': 'IPCC models systematically underestimate warming speed; observed warming 40% faster than median model projections (2000-2023)',
            'severity': 'critical',
            'factor': '~40% underestimation',
            'actual_vs_predicted': 'Actual: 1.2°C since 1850 vs IPCC median 2000 projection of 0.8°C by 2023',
            'evidence': 'Comparison of AR5/AR6 projections vs observed HadCRUT5 data; confirmed by multiple observatories',
            'source': 'IPCC AR6 WG1; NASA GISS'
        },
        {
            'domain': 'Climate Models',
            'category': 'Feedback Loops',
            'finding': 'Climate sensitivity models underestimate positive feedback amplification from ice-albedo loss and methane release',
            'severity': 'critical',
            'factor': '~2x underestimation of feedback strength',
            'actual_vs_predicted': 'Models: 3°C sensitivity vs Paleoclimate data: 4.5-6°C sensitivity',
            'evidence': 'Paleoclimate forcing analysis; recent ice sheet feedback observations',
            'source': 'Sherwood et al. 2020; Hansen & Sato 2012'
        },
        {
            'domain': 'Climate Models',
            'category': 'Non-Linearity',
            'finding': 'Models assume linear temperature response; observations show accelerating warming in certain thresholds',
            'severity': 'serious',
            'factor': '~1.5x underestimation in acceleration zones',
            'actual_vs_predicted': 'Models predict smooth curves; observed data shows step-change behavior at key tipping points',
            'evidence': 'Arctic amplification acceleration; abrupt sea ice loss events',
            'source': 'Arctic Report Card; NSIDC observations'
        },
        {
            'domain': 'Climate Models',
            'category': 'Compound Events',
            'finding': 'Models do not adequately capture compound climate hazards (simultaneous heat+drought+flood events)',
            'severity': 'serious',
            'factor': '~3-5x underestimation of compound event frequency',
            'actual_vs_predicted': 'Models: rare coincidence vs Reality: becoming seasonal in many regions',
            'evidence': '2021-2023 global compound event analysis; increasing temporal clustering',
            'source': 'Nature Climate Change; IPCC AR6 WG1'
        },
        # Sea Level Rise - 4 findings
        {
            'domain': 'Sea Level Rise',
            'category': 'Acceleration Rate',
            'finding': 'Sea level rise rate accelerating faster than predicted; models predict 0.4m by 2100, but current trajectory suggests 0.8-1.2m',
            'severity': 'critical',
            'factor': '~100-200% underestimation',
            'actual_vs_predicted': 'Current rate: 3.4mm/yr vs 2000 forecast of 1.7mm/yr',
            'evidence': 'Satellite sea level data 1993-2024; ice sheet discharge acceleration in Greenland/Antarctica',
            'source': 'NOAA Sea Level Rise Viewer; University of Colorado'
        },
        {
            'domain': 'Sea Level Rise',
            'category': 'Ice Sheet Instability',
            'finding': 'Antarctic ice sheet instability underestimated; marine ice sheet instability may be triggered at lower warming levels',
            'severity': 'critical',
            'factor': '~2-3x underestimation of discharge potential',
            'actual_vs_predicted': 'Models: gradual increase vs Observations: accelerating discharge from Twaites/Pine Island',
            'evidence': 'Twaites glacier velocity observations; ice sheet modeling updates',
            'source': 'Joughin et al. 2024; IMBIE consortium'
        },
        {
            'domain': 'Sea Level Rise',
            'category': 'Gravitational Effects',
            'finding': 'Gravitational redistribution of water mass from ice sheet melt creates regional variability; underestimated in coastal planning',
            'severity': 'serious',
            'factor': 'Regional factors create ±50% variation around global mean',
            'actual_vs_predicted': 'Planning assumes uniform rise; actual impacts highly location-dependent',
            'evidence': 'North Atlantic sea level rise exceeds global average; Pacific shows lower rise',
            'source': 'Frederikse et al. 2020; NOAA regional assessments'
        },
        {
            'domain': 'Sea Level Rise',
            'category': 'Subsidence Interaction',
            'finding': 'Local land subsidence from groundwater depletion amplifies sea level rise impacts; effect underestimated in risk assessments',
            'severity': 'serious',
            'factor': '~1-3m local subsidence possible by 2100 in coastal aquifer zones',
            'actual_vs_predicted': 'Sea level rise alone: 0.5-1m vs Combined with subsidence: 1.5-3m in vulnerable regions',
            'evidence': 'Jakarta, Venice, Tokyo subsidence patterns; aquifer depletion rates',
            'source': 'USGS subsidence studies; UNESCO groundwater reports'
        },
        # Biodiversity Loss - 4 findings
        {
            'domain': 'Biodiversity Loss',
            'category': 'Extinction Rate',
            'finding': 'Species extinction rate 100-1000x background rate; models predict single-digit % loss, but observed loss exceeds predictions',
            'severity': 'critical',
            'factor': '~5-10x underestimation',
            'actual_vs_predicted': 'Predicted: 5-15% extinction by 2100 vs Observed: already 68% decline in monitored populations',
            'evidence': 'Living Planet Index; IPBES Global Assessment; systematic underestimation of synergistic stressors',
            'source': 'WWF Living Planet Index; IPBES 2019'
        },
        {
            'domain': 'Biodiversity Loss',
            'category': 'Synergistic Stressors',
            'finding': 'Interaction of climate change with habitat loss, pollution, and overexploitation creates non-linear collapse dynamics',
            'severity': 'critical',
            'factor': '~10x underestimation when all stressors combined',
            'actual_vs_predicted': 'Models assess single stressors; combined stressor impacts multiply',
            'evidence': 'Pollinator decline acceleration; coral reef collapse synergies; insect biomass loss',
            'source': 'Hallmann et al. 2017; Ceballos et al. 2019'
        },
        {
            'domain': 'Biodiversity Loss',
            'category': 'Ecosystem Function Loss',
            'finding': 'Loss of ecosystem function precedes species extinction; carbon cycling, pollination, water cycling compromised before formal extinctions',
            'severity': 'critical',
            'factor': '~2-5 years earlier than predicted; impacts compound',
            'actual_vs_predicted': 'Species loss rate: 15-25% vs Functional loss rate: 30-50% in same timeframe',
            'evidence': 'Pollinator function decline; carbon sink capacity reduction in forests',
            'source': 'Dirzo & Raven 2003; Pan et al. 2013'
        },
        {
            'domain': 'Biodiversity Loss',
            'category': 'Spillover Effects',
            'finding': 'Biodiversity loss creates disease spillover acceleration (zoonotic pathogen emergence); underestimated pandemic risk',
            'severity': 'serious',
            'factor': '~5-10x underestimation of spillover event frequency',
            'actual_vs_predicted': 'Pre-2020 models: spillover events rare vs Post-2020: recognized as regular occurrence',
            'evidence': 'COVID-19 pandemic; increasing zoonotic disease emergence; habitat fragmentation drivers',
            'source': 'Dobson et al. 2020; UNEP Zoonotic Disease Report'
        },
        # Policy & Institutional - 4 findings
        {
            'domain': 'Policy Instruments',
            'category': 'NDC Gap',
            'finding': 'NDCs (Nationally Determined Contributions) calibrated for 2°C world; 3°C+ warming trajectory embedded in existing policies',
            'severity': 'critical',
            'factor': 'Policies designed for baseline that no longer exists',
            'actual_vs_predicted': 'Pledged actions → ~2.7°C warming; no major economy on track for own targets',
            'evidence': 'CAT (Climate Action Tracker) analysis; UNEP Emissions Gap Report 2023',
            'source': 'Climate Action Tracker; UNEP'
        },
        {
            'domain': 'Policy Instruments',
            'category': 'Implementation Failure',
            'finding': 'Policy-to-action gap widens; 10-20 year lag between policy adoption and measurable emissions reduction',
            'severity': 'critical',
            'factor': '~2 decades of delay in impact realization',
            'actual_vs_predicted': 'Policy ambition: net-zero by 2050 vs Actual trajectory: continued growth for 15-20 years',
            'evidence': 'Paris Agreement → actual emissions data tracking; IRA implementation timelines',
            'source': 'Global Carbon Project; Climate Analytics tracking'
        },
        {
            'domain': 'Policy Instruments',
            'category': 'Sectoral Mismatch',
            'finding': 'Hardest-to-decarbonize sectors (aviation, shipping, cement, steel) receive lowest policy attention and investment',
            'severity': 'serious',
            'factor': '~5-10x gap between emission level and mitigation investment',
            'actual_vs_predicted': 'Combined these sectors: 30% of emissions vs Mitigation investment: <5% of climate spending',
            'evidence': 'Climate finance tracking; sectoral emissions accounting',
            'source': 'OECD Climate Finance Report; IEA Net Zero Roadmap'
        },
        {
            'domain': 'Policy Instruments',
            'category': 'Rebound Effects',
            'finding': 'Efficiency improvements offset by increased consumption; energy efficiency gains lead to increased energy use (Jevons paradox)',
            'severity': 'serious',
            'factor': '~30-60% rebound effect negates policy gains',
            'actual_vs_predicted': 'Policy predicts emissions reduction; actual change much smaller due to consumption rebound',
            'evidence': 'Vehicle efficiency improvement vs total vehicle travel increase; home insulation vs heating fuel consumption',
            'source': 'Sorrell 2007; Galvin 2014'
        },
        # Economic Models - 3 findings
        {
            'domain': 'Economic Models',
            'category': 'Cost Assessment',
            'finding': 'Stern Review estimated climate damages at 5-20% of global GDP; newer assessments suggest 10-50% under severe scenarios',
            'severity': 'serious',
            'factor': '~2-5x underestimation',
            'actual_vs_predicted': 'Stern: 5% GDP loss vs Recent: tipping points @ 1.5-2°C involve non-linear economic collapse',
            'evidence': 'Transition risk models; compound systemic risk analysis; cascading failure economics',
            'source': 'ECB Financial Stability Review; transition risk literature'
        },
        {
            'domain': 'Economic Models',
            'category': 'Cascade Failures',
            'finding': 'Models underestimate cascade failure dynamics in interconnected global supply chains and financial systems',
            'severity': 'critical',
            'factor': '~3-10x underestimation of contagion speed',
            'actual_vs_predicted': 'Models: linear recession vs Reality: potential for compound systemic shocks (2008 financial crisis × climate)',
            'evidence': 'COVID-19 supply chain disruptions; 2022 energy crisis contagion; food price volatility',
            'source': 'World Bank risk assessments; transition risk finance reports'
        },
        {
            'domain': 'Economic Models',
            'category': 'Discount Rate Bias',
            'finding': 'Standard economic models use high discount rates that systematically undervalue future climate damages',
            'severity': 'serious',
            'factor': '~10-100x underestimation of long-term cost depending on discount rate choice',
            'actual_vs_predicted': '3% discount rate vs 0% or declining rates appropriate for irreversible losses',
            'evidence': 'Stern Review critique; debate over appropriate social discount rate for climate',
            'source': 'Weitzman 2007; Climate economics literature'
        },
        # Tipping Points - 3 findings
        {
            'domain': 'Tipping Points',
            'category': 'Cascade Dynamics',
            'finding': 'Tipping point thresholds estimated independently; cascading tipping point interaction systematically underestimated',
            'severity': 'critical',
            'factor': 'Non-linear cascade effects ignored',
            'actual_vs_predicted': 'Single tipping point assessment vs Cascading: Amazon→AMOC→monsoon feedback loops',
            'evidence': 'Steffen et al. 2018 tipping cascade analysis; Earth system tipping points paper',
            'source': 'Steffen et al. 2018; Lenton et al. 2019'
        },
        {
            'domain': 'Tipping Points',
            'category': 'Threshold Uncertainty',
            'finding': 'Tipping point thresholds have wide confidence ranges; actual thresholds may be 0.5-1°C lower than central estimates',
            'severity': 'critical',
            'factor': '~1-2°C threshold shift means already passed or very close for several systems',
            'actual_vs_predicted': 'Amazon tipping point: estimated 3-5°C vs emerging evidence: possibly <2°C',
            'evidence': 'Amazonian dieback modeling uncertainty; AMOC collapse threshold debates',
            'source': 'Zemp et al. 2018; Caesar et al. 2021'
        },
        {
            'domain': 'Tipping Points',
            'category': 'Early Warning Signals',
            'finding': 'Early warning signals for tipping points are weak and difficult to detect; systems may cross thresholds with minimal advance notice',
            'severity': 'serious',
            'factor': '~1-5 year detection lag before point of no return crossed',
            'actual_vs_predicted': 'Theory suggests early warning windows; empirical detection remains unreliable',
            'evidence': 'Arctic sea ice tipping point; Greenland ice sheet acceleration without clear warning',
            'source': 'Scheffer et al. 2009; paleoclimate abrupt change records'
        },
        # Measurement Systems - 3 findings
        {
            'domain': 'Measurement Systems',
            'category': 'Data Loss',
            'finding': 'Ocean monitoring infrastructure declining; satellite data gaps expanding in access-constrained regions',
            'severity': 'serious',
            'factor': 'Measurement capacity degradation increases underestimation of regional crises',
            'actual_vs_predicted': 'Pre-2023: comprehensive monitoring vs Post-2023: NSIDC ice sheets service discontinued; gaps expanding',
            'evidence': 'Loss of direct ocean monitoring buoys; satellite constellation degradation',
            'source': 'NSIDC; Argo array monitoring'
        },
        {
            'domain': 'Measurement Systems',
            'category': 'Regional Blind Spots',
            'finding': 'Measurement gaps in Global South create asymmetric knowledge; climate impacts in developing regions underestimated due to monitoring gaps',
            'severity': 'serious',
            'factor': '~50% underestimation of impacts in under-monitored regions',
            'actual_vs_predicted': 'Northern Hemisphere data rich; African, South Asian impacts poorly quantified',
            'evidence': 'Sparse weather station networks in Africa/South Asia; limited satellite access in some regions',
            'source': 'WMO Global Cryosphere Watch; IPCC Chapter on regional impacts'
        },
        {
            'domain': 'Measurement Systems',
            'category': 'Lag Time',
            'finding': 'Data from satellite and ground observations lags 1-3 years behind real-time events; by the time crisis is documented, it has already evolved',
            'severity': 'moderate',
            'factor': '~2 year lag in understanding current state',
            'actual_vs_predicted': 'Real-time reality vs Documented historical data creates perpetual information lag',
            'evidence': 'Annual carbon cycle accounting delays; ice sheet velocity updates; ocean temperature lag',
            'source': 'Global Carbon Project reporting cycles; satellite data processing pipelines'
        },
        # Institutional Adaptation - 3 findings
        {
            'domain': 'Institutional Adaptation',
            'category': 'Lag Time',
            'finding': 'Policy response lag systematically underestimated; 10-20 year implementation delay in major institutions',
            'severity': 'serious',
            'factor': 'Response lag creates 20-40 year window of unmitigated change',
            'actual_vs_predicted': 'Institutional change cycles much longer than climate crisis acceleration cycles',
            'evidence': 'Paris Agreement → actual policy implementation delay; IRA implementation timelines',
            'source': 'Government policy tracking; institutional change literature'
        },
        {
            'domain': 'Institutional Adaptation',
            'category': 'Maladaptation Risk',
            'finding': 'Adaptation projects designed for historical climate conditions; infrastructure built now will fail under 2050+ conditions',
            'severity': 'critical',
            'factor': '~1-2 decade lifespan mismatch for long-lived infrastructure',
            'actual_vs_predicted': 'Infrastructure designed for 20th century climate + modest warming vs 21st century accelerating change',
            'evidence': 'Dams designed for historical precipitation patterns failing; coastal infrastructure already compromised',
            'source': 'IPCC AR6 WG2; maladaptation assessment studies'
        },
        {
            'domain': 'Institutional Adaptation',
            'category': 'Social Equity Gaps',
            'finding': 'Adaptation investment flows to wealthy regions/sectors; vulnerable populations have minimal adaptation capacity',
            'severity': 'serious',
            'factor': '~20-50x gap between adaptation needs and available capital in Global South',
            'actual_vs_predicted': 'Adaptation finance: $30B annually vs Estimated needs: $300B+ annually',
            'evidence': 'Climate finance flows tracking; adaptation gap reports; vulnerability indices',
            'source': 'UNEP Adaptation Gap Report; World Bank climate finance tracking'
        },
    ]

    conn = get_connection()
    c = conn.cursor()

    count = 0
    for f in findings:
        try:
            c.execute('''INSERT INTO systematic_underestimation
                         (domain, category, finding_text, severity, underestimation_factor,
                          actual_vs_predicted, evidence_text, source, status)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (f['domain'], f['category'], f['finding'], f['severity'],
                       f['factor'], f['actual_vs_predicted'], f['evidence'], f['source'], 'active'))
            count += 1
        except Exception as e:
            print(f"⚠ Error adding underestimation finding: {e}")

    conn.commit()
    conn.close()
    print(f"✓ Imported {count} systematic underestimation findings")
    return count

def import_research_findings():
    """Import backdated research findings organized by mechanism"""
    findings = [
        # Threshold Dynamics
        {
            'mechanism': 'Threshold Dynamics',
            'finding': 'Cascade nodes demonstrate activation thresholds below which systems appear stable but are increasingly fragile',
            'confidence': 0.85,
            'evidence': 'Signal amplitude tracking across 13 cascade nodes; phase transition behavior observed in baseline failures',
            'signals': 'Multiple signal clusters showing nonlinear behavior before threshold crossing'
        },
        {
            'mechanism': 'Threshold Dynamics',
            'finding': 'Thresholds are dynamic and shifting—past baselines no longer predict future system behavior',
            'confidence': 0.88,
            'evidence': 'Baseline return failures increasing; historical standards no longer applicable to current conditions',
            'signals': 'Baseline shift patterns across geographies and sectors'
        },
        # Feedback Amplification
        {
            'mechanism': 'Feedback Amplification',
            'finding': 'Measurement capacity erosion creates positive feedback: less visibility → poorer response → more degradation → less visibility',
            'confidence': 0.82,
            'evidence': 'NSIDC ice sheet monitoring discontinued; satellite data gaps expanding; measurement systems degrading',
            'signals': 'Infrastructure brittleness node activity; rate of change acceleration'
        },
        {
            'mechanism': 'Feedback Amplification',
            'finding': 'Economic depletion feedback loop: crisis response exhausts capital → reduced capacity for next crisis → cascading failures',
            'confidence': 0.80,
            'evidence': 'Continuous disaster response funding; emergency budgets becoming permanent; adaptation exhaustion patterns',
            'signals': 'Economic depletion node showing sustained amplitude growth'
        },
        {
            'mechanism': 'Feedback Amplification',
            'finding': 'Cascade failure amplification through system coupling: single-node failures trigger cascades across interdependent systems',
            'confidence': 0.84,
            'evidence': 'CASCADE sequences 1-12 showing multi-node activation patterns; coordination failure node critical',
            'signals': '50+ identified signals; 12 CASCADE sequences; high interconnectedness'
        },
        # Institutional Lag
        {
            'mechanism': 'Institutional Lag',
            'finding': 'Policy instruments systematically miscalibrated: NDCs designed for 2°C warming but trajectory is 3°C+',
            'confidence': 0.89,
            'evidence': 'Climate Action Tracker analysis; Paris Agreement implementation gaps; policy-reality divergence',
            'signals': 'Regulatory capture and institutional suppression nodes; policy lag patterns'
        },
        {
            'mechanism': 'Institutional Lag',
            'finding': 'Institutional adaptation lag is 10-20 years; climate acceleration is 5-10 year cycles; gap is structural',
            'confidence': 0.86,
            'evidence': 'Change/adaptation lag node; rate of change node; scenario planning collapse patterns',
            'signals': 'Adaptation exhaustion; change lag node showing increasing frequency'
        },
        {
            'mechanism': 'Institutional Lag',
            'finding': 'Scenario planning systems optimized for "solvable pathways"; institutional rejection of transformative scenarios',
            'confidence': 0.79,
            'evidence': 'Scenario planning collapse node; institutional suppression patterns in model outputs',
            'signals': 'Automatic denial mechanisms; regulatory capture preventing major shifts'
        },
        # Measurement & Uncertainty
        {
            'mechanism': 'Measurement & Uncertainty',
            'finding': '8 critical domains show systematic 5x-100x underestimation of severity: climate models, sea level rise, biodiversity, tipping points',
            'confidence': 0.87,
            'evidence': 'IPCC 40% warming speed underestimation; biodiversity loss 5-10x underestimated vs observed 68% population decline',
            'signals': 'Measurement capacity erosion node; systematic underestimation tracking page'
        },
        {
            'mechanism': 'Measurement & Uncertainty',
            'finding': 'Economic cost underestimation 2-5x: Stern Review 5% GDP vs current 10-50% assessments under severe scenarios',
            'confidence': 0.83,
            'evidence': 'ECB Financial Stability Review; transition risk models; compound systemic risk analysis',
            'signals': 'Economic depletion node; reference point tracking showing cost escalation'
        },
        # Tipping Points & Bifurcation
        {
            'mechanism': 'Tipping Points & Bifurcation',
            'finding': 'Individual tipping points underestimated; cascading tipping point interactions completely absent from standard models',
            'confidence': 0.85,
            'evidence': 'Steffen et al. 2018; Amazon→AMOC→monsoon feedback loops not in standard climate assessments',
            'signals': 'Cascade node interactions showing amplification patterns'
        },
        {
            'mechanism': 'Tipping Points & Bifurcation',
            'finding': 'Thresholds becoming new floors: disaster events reset system baselines to lower levels; previous recovery impossible',
            'confidence': 0.84,
            'evidence': 'Baseline return failure patterns; irreversible state transitions in water/agriculture/infrastructure systems',
            'signals': 'Baseline failures expanding; thresholds becoming floors node activity'
        },
        # Coupling & Interdependence
        {
            'mechanism': 'Coupling & Interdependence',
            'finding': 'Infrastructure brittleness: systems built for stable climate now fail under change; built-in fragility increasing',
            'confidence': 0.86,
            'evidence': 'Heatwave failures of infrastructure; water scarcity impacts on food-energy-water nexus',
            'signals': 'Infrastructure brittleness and coordination cascade failure nodes active'
        },
        {
            'mechanism': 'Coupling & Interdependence',
            'finding': 'Water bankruptcy emerging: transition from water abundance to scarcity-based management in multiple geographies',
            'confidence': 0.81,
            'evidence': 'Groundwater depletion patterns; river system failures; aquifer collapse in agricultural regions',
            'signals': 'Water bankruptcy node; baseline failures in water-dependent sectors'
        },
        # Socioeconomic Constraints
        {
            'mechanism': 'Socioeconomic Constraints',
            'finding': 'Economic constraints limit adaptation speed: continuous crisis response exhausts capital; transformation capacity declining',
            'confidence': 0.80,
            'evidence': 'Disaster relief costs escalating; infrastructure maintenance backlogs growing; adaptation funding insufficient',
            'signals': 'Economic depletion node; adaptation exhaustion patterns'
        },
        {
            'mechanism': 'Socioeconomic Constraints',
            'finding': 'Rate of change exceeds adaptive capacity: system change acceleration outpacing institutional and social response',
            'confidence': 0.82,
            'evidence': 'Rate of change acceleration documented; adaptation lag increasing; scenario planning inadequacy',
            'signals': 'Rate of change node; adaptation exhaustion node'
        },
        # Information Asymmetry
        {
            'mechanism': 'Information Asymmetry',
            'finding': 'Measurement systems degrading: monitoring capacity loss increases information asymmetry and deepens blind spots',
            'confidence': 0.83,
            'evidence': 'NSIDC service discontinuation; satellite constellation degradation; Argo array gaps',
            'signals': 'Measurement capacity erosion node; data access loss in critical regions'
        },
        {
            'mechanism': 'Information Asymmetry',
            'finding': 'Scenario planning collapse: models systematically exclude worst-case pathways; optimism bias embedded in analysis',
            'confidence': 0.78,
            'evidence': 'Published scenarios show concentration on "solvable" outcomes; transformative scenarios underrepresented',
            'signals': 'Scenario planning collapse node; institutional suppression patterns'
        },
    ]

    conn = get_connection()
    c = conn.cursor()

    count = 0
    for f in findings:
        try:
            c.execute('''INSERT INTO research_findings
                         (mechanism, finding_text, confidence_level, supporting_evidence,
                          related_signals, status)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (f['mechanism'], f['finding'], f['confidence'], f['evidence'],
                       f['signals'], 'active'))
            count += 1
        except Exception as e:
            print(f"⚠ Error adding research finding: {e}")

    conn.commit()
    conn.close()
    print(f"✓ Imported {count} research findings across 8 mechanisms")
    return count

def import_august_2026_signals():
    """Import August 2026 headline signals (test drive with real-world data)"""
    signals_data = [
        # Feedback Amplification signals (Node 10: Coordination Cascade Failure)
        {'node': 10, 'domain': 'Temperature Records', 'description': 'July 2026: Hottest month globally + US oceans; records from 100+ years broken', 'severity': 'critical', 'date': '2026-08-13', 'source': 'Gizmodo'},
        {'node': 10, 'domain': 'Heat Persistence', 'description': 'Europe heat dome 40°C+ recurring pattern; system lock-in to high-heat regime', 'severity': 'critical', 'date': '2026-08-14', 'source': 'Severe Weather Europe'},
        {'node': 10, 'domain': 'El Niño Coupling', 'description': '2026 tracking 2nd-warmest year on record; strong El Niño amplifying warming', 'severity': 'serious', 'date': '2026-08-13', 'source': 'Carbon Brief'},
        {'node': 10, 'domain': 'Drought Cascade', 'description': 'Multi-continent drought: Americas, Europe, Africa; water depletion creating $100B+ losses', 'severity': 'critical', 'date': '2026-08-05', 'source': 'Godfrey Daily'},
        {'node': 10, 'domain': 'Economic Compounding', 'description': 'H1 2026: $100B in climate-related economic losses; multiple simultaneous disasters', 'severity': 'critical', 'date': '2026-08-01', 'source': 'Swiss Re'},
        {'node': 10, 'domain': 'Heat Records Accelerating', 'description': 'South US heat wave: dozens of records broken in single week', 'severity': 'serious', 'date': '2026-08-14', 'source': 'Weather.com'},
        {'node': 10, 'domain': 'Economic Disruption', 'description': 'Heat, fire, smoke, storms simultaneously wreaking havoc on US economy', 'severity': 'critical', 'date': '2026-08-14', 'source': 'Guy On Climate'},
        {'node': 10, 'domain': 'European Economic Crisis', 'description': 'Europe blowing up riverbeds, destroying shipping infrastructure due to extreme drought', 'severity': 'critical', 'date': '2026-08-05', 'source': 'CNBC'},

        # Threshold Dynamics signals (Node 5: Thresholds Becoming Floors)
        {'node': 5, 'domain': 'Biodiversity Extinction', 'description': '8,000 species face extinction from climate impacts; tipping point approaching', 'severity': 'critical', 'date': '2026-08-10', 'source': 'Down to Earth'},
        {'node': 5, 'domain': 'Water Depletion Thresholds', 'description': 'Global droughts reaching new limits; multiple regions crossing water scarcity thresholds', 'severity': 'critical', 'date': '2026-08-06', 'source': 'World Resources'},
        {'node': 5, 'domain': 'Ecosystem Collapse', 'description': 'Biodiversity decline accelerating despite recovery efforts; institutional responses inadequate', 'severity': 'critical', 'date': '2026-08-12', 'source': 'Taylor & Francis'},

        # Water Bankruptcy signals (Node 1: Water Bankruptcy)
        {'node': 1, 'domain': 'Water Scarcity Crisis', 'description': 'Europe severe drought destroying river ecosystems; water system transition to scarcity management', 'severity': 'critical', 'date': '2026-08-05', 'source': 'CNBC'},
        {'node': 1, 'domain': 'Compound Water Stress', 'description': 'Simultaneous droughts across Americas, Europe, Asia; global synchronized water stress', 'severity': 'critical', 'date': '2026-08-06', 'source': 'Global Water Council'},
        {'node': 1, 'domain': 'Infrastructure Destruction', 'description': 'European riverbeds destroyed; shipping channels inoperable due to water depletion', 'severity': 'serious', 'date': '2026-08-05', 'source': 'CNBC'},

        # Institutional Lag signals (Node 3: Institutional Suppression + Node 13: Change/Adaptation Lag)
        {'node': 3, 'domain': 'Policy Implementation Failure', 'description': 'Nearly 50 countries still missing UN climate plans 18 months past deadline', 'severity': 'critical', 'date': '2026-08-06', 'source': 'Climate Change News'},
        {'node': 3, 'domain': 'NDC Insufficiency', 'description': 'New climate plans fall short of Paris goals; 2.7-3°C+ trajectory embedded in policies', 'severity': 'critical', 'date': '2026-08-01', 'source': 'World Resources Institute'},
        {'node': 13, 'domain': 'Adaptation Gap', 'description': 'Infrastructure designed for historical climate failing under compound hazards', 'severity': 'critical', 'date': '2026-08-10', 'source': 'Coastal Adaptation Reports'},
        {'node': 13, 'domain': 'Single-Hazard Infrastructure', 'description': 'Coastal and flood infrastructure designed for single hazards; fails under compound events', 'severity': 'serious', 'date': '2026-08-15', 'source': 'Yale Climate Connections'},

        # Compound Event Cascades signals (Node 10: Coordination Cascade Failure)
        {'node': 10, 'domain': 'Compound Flooding', 'description': 'Storm surge + sea level rise + rainfall creating cascading infrastructure failures', 'severity': 'critical', 'date': '2026-08-12', 'source': 'Yale Climate Connections'},
        {'node': 10, 'domain': 'Coastal Subsidence + SLR', 'description': 'Coastal cities sinking faster than oceans rising; compound subsidence effect accelerates inundation', 'severity': 'critical', 'date': '2026-08-01', 'source': 'ScienceDaily'},
        {'node': 10, 'domain': 'Multi-Hazard Cascade', 'description': 'Heat dome + extreme rainfall + flooding occurring simultaneously in multiple regions', 'severity': 'critical', 'date': '2026-08-14', 'source': 'Weather.com'},
        {'node': 10, 'domain': 'Supply Chain Disruption', 'description': 'Compound disasters (heat+fire+smoke+storms) creating cascading supply chain failures', 'severity': 'serious', 'date': '2026-08-14', 'source': 'Guy On Climate'},

        # Rate of Change signals (Node 4: Rate of Change)
        {'node': 4, 'domain': 'Record Acceleration', 'description': 'Temperature records breaking monthly; historical norms completely insufficient for 2026 conditions', 'severity': 'critical', 'date': '2026-08-13', 'source': 'WMO'},
        {'node': 4, 'domain': 'Simultaneous Global Events', 'description': 'Multiple simultaneous regional crises (US heat, Europe drought, Asian flooding) indicate system-wide acceleration', 'severity': 'critical', 'date': '2026-08-14', 'source': 'Multiple outlets'},

        # Infrastructure Brittleness signals (Node 8: Infrastructure Brittleness)
        {'node': 8, 'domain': 'Infrastructure Failure', 'description': 'Shipping channels destroyed, roads damaged by compound hazards; infrastructure built for stable climate failing', 'severity': 'critical', 'date': '2026-08-05', 'source': 'CNBC'},
        {'node': 8, 'domain': 'Coastal Infrastructure Compromise', 'description': 'Coastal defense systems overwhelmed; subsidence + sea level rise creating breaches', 'severity': 'serious', 'date': '2026-08-10', 'source': 'Coastal Engineering'},

        # Economic Depletion signals (Node 7: Economic Depletion)
        {'node': 7, 'domain': 'Crisis Response Costs', 'description': 'H1 2026 disaster losses hit $100B; continuous crisis response depleting capital reserves', 'severity': 'critical', 'date': '2026-08-01', 'source': 'Swiss Re'},
        {'node': 7, 'domain': 'Compounding Economic Losses', 'description': 'Multiple simultaneous economic impacts (drought, heat, flooding) compounding losses beyond mitigation capacity', 'severity': 'critical', 'date': '2026-08-14', 'source': 'Partnership for Responsible Growth'},

        # Scenario Planning Collapse signals (Node 9: Scenario Planning Collapse)
        {'node': 9, 'domain': 'Plan Insufficiency', 'description': 'Published climate plans demonstrably insufficient; reality outpacing scenario projections', 'severity': 'critical', 'date': '2026-08-01', 'source': 'World Resources Institute'},

        # Measurement signals (Node 6: Measurement Capacity Erosion)
        {'node': 6, 'domain': 'Data Lag', 'description': 'Real-time climate reality outpacing documented historical data; information lag building blindness', 'severity': 'serious', 'date': '2026-08-15', 'source': 'Global Carbon Project'},
    ]

    conn = get_connection()
    c = conn.cursor()

    count = 0
    for signal in signals_data:
        try:
            c.execute('''INSERT INTO signals
                         (node_id, domain, description, severity, date_recorded, source, status)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (signal['node'], signal['domain'], signal['description'],
                       signal['severity'], signal['date'], signal['source'], 'active'))
            count += 1
        except Exception as e:
            print(f"⚠ Error adding signal: {e}")

    conn.commit()
    conn.close()
    print(f"✓ Imported {count} signals from August 2026 headline scan")
    return count

def import_reference_points():
    """Import system robustness baseline reference points"""
    from cascade_db import add_reference_point

    reference_points = [
        {
            'metric': 'System Robustness - Initial Baseline',
            'value': 78.0,
            'category': 'System Health',
            'date': '2026-01-01'
        },
        {
            'metric': 'System Robustness - Q1 2026',
            'value': 72.5,
            'category': 'System Health',
            'date': '2026-03-31'
        },
        {
            'metric': 'System Robustness - Q2 2026',
            'value': 65.0,
            'category': 'System Health',
            'date': '2026-06-30'
        },
        {
            'metric': 'System Robustness - Current',
            'value': 58.0,
            'category': 'System Health',
            'date': '2026-08-18'
        },
    ]

    count = 0
    for point in reference_points:
        try:
            add_reference_point(point['metric'], point['value'], point['category'], point['date'])
            count += 1
        except Exception as e:
            print(f"⚠ Error adding reference point: {e}")

    print(f"✓ Imported {count} system robustness reference points")
    return count

def initialize_and_import():
    """Run importers on first startup only; subsequent restarts skip to prevent duplication"""
    print("\n🚀 Starting Project Cascade Database...\n")

    init_db()
    print("✓ Database schema initialized")

    # Check if database already has data
    conn = get_connection()
    c = conn.cursor()
    existing_signals = c.execute('SELECT COUNT(*) FROM signals').fetchone()[0]
    conn.close()

    if existing_signals > 0:
        # Database already populated; skip re-import to prevent duplication
        print("\n✓ Database already populated with data")
        print("  (File watcher will handle incremental updates)")
    else:
        # First startup; run all imports
        print("\n📥 Populating database for first time...\n")

        import_cascade_nodes()
        import_from_confluence_state()
        import_cascade_sequences()
        import_baseline_failures()
        import_signals_from_confluence()
        import_signals_from_cascading_nodes_log()
        import_signals_from_dan_evidence()
        import_signals_from_daily_findings()
        import_amplitude_watch()
        import_daily_findings()
        import_systematic_underestimations()
        import_research_findings()
        import_reference_points()
        import_august_2026_signals()

        print("\n✅ Import complete!")

    # Display summary (always)
    conn = get_connection()
    c = conn.cursor()

    nodes = c.execute('SELECT COUNT(*) FROM cascade_nodes').fetchone()[0]
    signals = c.execute('SELECT COUNT(*) FROM signals').fetchone()[0]
    cascades = c.execute('SELECT COUNT(*) FROM cascade_sequences').fetchone()[0]
    baselines = c.execute('SELECT COUNT(*) FROM baseline_failures').fetchone()[0]
    ref_points = c.execute('SELECT COUNT(*) FROM reference_points').fetchone()[0]
    findings = c.execute('SELECT COUNT(*) FROM research_findings').fetchone()[0]

    conn.close()

    print(f"\nDatabase Status:")
    print(f"  • Cascade Nodes: {nodes}")
    print(f"  • Signals: {signals}")
    print(f"  • CASCADE Sequences: {cascades}")
    print(f"  • Baseline Failures: {baselines}")
    print(f"  • Reference Points: {ref_points}")
    print(f"  • Research Findings: {findings}")

if __name__ == '__main__':
    initialize_and_import()
