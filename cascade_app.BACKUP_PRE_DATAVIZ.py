# -*- coding: utf-8 -*-
"""
Project Cascade Standalone Application
Streamlit-based dashboard with 8 primary sections
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from cascade_db import (
    get_all_nodes, get_all_signals, get_cascade_sequences,
    get_reference_points, get_baseline_failures, get_metrics_summary,
    get_node_signals, get_daily_findings, get_nodes_by_activity,
    get_cascade_sequences_with_signals, get_geographic_hotspots,
    get_system_robustness_trajectory, get_all_reference_points_latest,
    get_amplitude_watch, get_amplitude_watch_by_status,
    get_all_goals, add_goal, update_goal, retire_goal, activate_goal,
    get_all_underestimations, get_underestimations_by_category, add_underestimation,
    get_underestimation_domains, get_underestimation_summary,
    get_all_findings, get_findings_by_mechanism, add_finding, get_mechanisms_list, get_findings_summary
)
import json

# Page config
st.set_page_config(
    page_title="Project Cascade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme
st.markdown("""
    <style>
    :root {
        --surface-1: #1a1a19;
        --text-primary: #ffffff;
        --text-secondary: #c3c2b7;
        --series-1: #3987e5;
    }
    body {
        background-color: #0d0d0d;
        color: #ffffff;
        font-size: 18px;
    }

    /* Increase font sizes globally by +2 */
    h1 { font-size: 2.5em !important; }
    h2 { font-size: 2.0em !important; }
    h3 { font-size: 1.75em !important; }
    p, li, div { font-size: 18px !important; }

    /* Highlight for recent additions */
    .highlight-recent {
        background-color: #8B6F47;
        padding: 12px;
        border-radius: 6px;
        margin: 8px 0;
        border-left: 4px solid #D4A574;
        color: #f0f0f0;
    }

    .highlight-recent strong {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

def metric_card(label, value, trend=None, color="#3987e5"):
    """Render a metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label, value)
    if trend:
        with col2:
            st.caption(trend)

# ============================================
# 1. SUMMARY
# ============================================
def section_summary():
    st.header("📋 Project Summary — System Health Dashboard")

    # Get all data
    metrics = get_metrics_summary()
    nodes_by_activity = get_nodes_by_activity()
    cascades_with_signals = get_cascade_sequences_with_signals()
    hotspots = get_geographic_hotspots()
    reference_points = get_all_reference_points_latest()

    # Executive Summary Metrics (Top Row)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Signals", metrics['total_signals'])
    with col2:
        active_count = len([n for n in nodes_by_activity if n['status'] == 'active'])
        st.metric("Active Nodes", active_count)
    with col3:
        st.metric("CASCADE Sequences", metrics['cascade_sequences'])
    with col4:
        st.metric("Geographic Hotspots", len(hotspots))
    with col5:
        robustness = next((rp['value'] for rp in reference_points if 'Robustness' in rp['metric_name']), 0)
        st.metric("System Robustness", f"{robustness:.0f}%")

    st.divider()

    # Section 1: Top Activated Nodes (Ranked by Signal Count & Severity)
    st.subheader("🔴 Top Activated Cascade Nodes")
    st.caption("Ranked by signal frequency and severity — nodes with greatest real-world activation")

    active_nodes = [n for n in nodes_by_activity if n['status'] == 'active']
    if active_nodes:
        node_display = []
        for node in active_nodes[:8]:  # Top 8
            node_display.append({
                'Node': f"Node {node['node_id']}",
                'Mechanism': node['name'],
                'Signals': node['signal_count'] or 0,
                'Severity': node['severity_score'] or 0,
                'Amplitude': f"{node['amplitude']:.1f}" if node['amplitude'] else "—",
                'Frequency': f"{node['frequency']:.1f}" if node['frequency'] else "—"
            })

        node_df = pd.DataFrame(node_display)
        st.dataframe(node_df, width='stretch', hide_index=True)
    else:
        st.info("No active nodes currently being tracked")

    st.divider()

    # Section 2: Active CASCADE Sequences with Real-World Confirmations
    st.subheader("🔗 Active CASCADE Sequences")
    st.caption("CASCADE pathways showing real-world activation — documented causal chains")

    if cascades_with_signals:
        cascade_display = []
        for cs in cascades_with_signals[:10]:
            cascade_display.append({
                'ID': f"CASCADE {cs['cascade_id']}",
                'Node Chain': cs['node_sequence'],
                'Real-World Signals': cs['signal_count'] or 0,
                'Confidence': f"{cs['confidence']:.0%}" if cs['confidence'] else "—"
            })

        cascade_df = pd.DataFrame(cascade_display)
        st.dataframe(cascade_df, width='stretch', hide_index=True)
    else:
        st.info("No CASCADE sequences with signals yet")

    st.divider()

    # Section 3: Geographic Hotspots of Baseline Return Failures
    st.subheader("🌍 Geographic Hotspots — Baseline Return Failure Expansion")
    st.caption("Regions/sectors showing persistent inability to return to pre-disaster baseline")

    if hotspots:
        hotspot_display = []
        for spot in hotspots:
            hotspot_display.append({
                'Region/Sector': spot['geography'],
                'Failures Documented': spot['failure_count'],
                'Avg Baseline Shift %': f"{spot['avg_shift']:.1f}%",
                'Range': f"{spot['min_shift']:.0f}% to {spot['max_shift']:.0f}%"
            })

        hotspot_df = pd.DataFrame(hotspot_display)
        st.dataframe(hotspot_df, width='stretch', hide_index=True)
    else:
        st.info("No baseline failures documented yet")

    st.divider()

    # Section 4: System Robustness Trajectory
    st.subheader("📉 System Robustness Trajectory")
    st.caption("Degradation trend — is system adaptive capacity declining?")

    robustness_data = get_system_robustness_trajectory()
    if robustness_data:
        robust_df = pd.DataFrame(robustness_data)
        robust_df['date_recorded'] = pd.to_datetime(robust_df['date_recorded'])

        fig = px.line(robust_df, x='date_recorded', y='value',
                     title="System Robustness Over Time",
                     markers=True)
        fig.update_layout(height=300)
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Robustness Index (%)")
        st.plotly_chart(fig)
    else:
        st.info("Insufficient robustness data for trend analysis")

    st.divider()

    # Section 5: Reference Points (System-Level Metrics)
    st.subheader("📊 System-Level Reference Points")
    st.caption("Amplitude, Frequency, Interconnectedness, Underestimation, and Robustness metrics")

    if reference_points:
        ref_display = []
        for rp in reference_points:
            ref_display.append({
                'Metric': rp['metric_name'],
                'Value': f"{rp['value']:.1f}",
                'Last Updated': rp['date_recorded']
            })

        ref_df = pd.DataFrame(ref_display)
        st.dataframe(ref_df, width='stretch', hide_index=True)
    else:
        st.info("No reference points recorded yet")

    st.divider()

    # Section 6: Recent Signals (Last 20)
    st.subheader("📌 Recent Signals (Last 20)")
    st.caption("Latest cascade mechanism activations — ordered by date")

    signals = get_all_signals(limit=20)
    if signals:
        signals_df = pd.DataFrame(signals)
        signals_df['date_recorded'] = pd.to_datetime(signals_df['date_recorded'])
        display_cols = ['node_id', 'domain', 'severity', 'source', 'date_recorded']
        signals_df = signals_df[display_cols]
        signals_df.columns = ['Node', 'Domain', 'Severity', 'Source', 'Date']
        st.dataframe(signals_df, width='stretch', hide_index=True)
    else:
        st.info("No signals recorded yet")

# ============================================
# 2. TODAY'S PROGRESS
# ============================================
def section_today_progress():
    st.header("📈 Today's Progress")

    today_str = datetime.now().strftime('%Y-%m-%d')

    # Get daily findings
    findings_data = get_daily_findings(today_str)

    # Determine if finding is from news scan
    def is_news_scan_item(text):
        return 'HEADLINE NEWS SCAN' in text or any(
            pattern in text for pattern in [
                'UCS Report:', 'The Ecologist:', 'UN/', 'Green Climate Fund:',
                'Oxfam:', 'Ocean monitoring:', 'Satellite gap:', 'Data gaps:',
                'Canada:', 'UK:'
            ]
        )

    if findings_data:
        st.subheader("Daily Overview")
        st.markdown(findings_data['overview'])

        st.divider()

        # Findings
        if findings_data['findings']:
            st.subheader("📍 Findings")
            findings_list = json.loads(findings_data['findings'])
            if findings_list:
                for finding in findings_list:
                    if is_news_scan_item(finding):
                        st.markdown(f'<div class="highlight-recent">• <strong>{finding}</strong></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"• {finding}")
            else:
                st.info("No findings recorded yet today")

        st.divider()

        # Methodological Insights
        if findings_data['methodological_insights']:
            st.subheader("🔧 Methodological Insights")
            insights_list = json.loads(findings_data['methodological_insights'])
            if insights_list:
                for insight in insights_list:
                    st.markdown(f"• {insight}")
            else:
                st.info("No methodological insights recorded yet")

        st.divider()

        # Theoretical Model Advances
        if findings_data['theoretical_advances']:
            st.subheader("🧠 Theoretical Model Advances")
            advances_list = json.loads(findings_data['theoretical_advances'])
            if advances_list:
                for advance in advances_list:
                    if 'CONFIRMED' in advance or 'NEW INSTANCE' in advance or 'Node' in advance[:20]:
                        st.markdown(f'<div class="highlight-recent">• <strong>{advance}</strong></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"• {advance}")
            else:
                st.info("No theoretical advances recorded yet")

        st.divider()

        # Timestamp
        st.caption(f"📝 Last updated: {findings_data['last_updated']}")

    else:
        st.info(f"No daily findings recorded for {today_str}. Add entries to `daily_findings.md` to get started.")

# ============================================
# 3. MISSION AND GOALS
# ============================================
def section_mission_goals():
    st.header("🎯 Mission and Goals")

    st.subheader("Framework")
    st.markdown("""
    **Project Cascade** tracks 13 mechanisms documenting how constrained systems fail sequentially.

    **13 Cascade Nodes:**
    1. Water Bankruptcy
    2. Regulatory Capture
    3. Institutional Suppression
    4. Rate of Change
    5. Thresholds Becoming Floors
    6. Measurement Capacity Erosion
    7. Economic Depletion
    8. Infrastructure Brittleness
    9. Scenario Planning Collapse
    10. Coordination Cascade Failure
    11. Infrastructure Built for Still Climate
    12. Adaptation Exhaustion
    13. Change/Adaptation Lag
    """)

    st.divider()

    st.subheader("Primary Goals")
    st.markdown("""
    1. **Systematic Observation** - Document cascade mechanism activation and amplification
    2. **Signal Integration** - Integrate research findings into framework without artificial delays
    3. **Baseline Return Tracking** - Monitor post-disaster recovery failures across sectors
    4. **Early Detection** - Identify cascade sequences before they lock in irreversibly
    5. **Real-time Monitoring** - Track amplitude, frequency, and interconnectedness metrics
    """)

    st.divider()

    st.subheader("Reference Points")
    ref_points = get_reference_points()
    if ref_points:
        # Get latest values for each metric
        metrics_latest = {}
        for rp in ref_points:
            metric = rp['metric_name']
            if metric not in metrics_latest or rp['date_recorded'] > metrics_latest[metric]['date_recorded']:
                metrics_latest[metric] = rp

        for metric, data in metrics_latest.items():
            st.metric(metric, f"{data['value']:.1f}")
    else:
        st.info("No reference points recorded yet")

# ============================================
# 4. AMPLITUDE
# ============================================
def section_amplitude():
    st.header("⚡ Amplitude Watch Log")

    st.markdown("""
    **Tracks whether individual cascade mechanisms are escalating in scale, severity, or impact.**

    Complements the PC Map (which documents mechanism presence) by monitoring mechanism **intensification**.
    Distinguishes between mechanisms that are simply active vs. mechanisms that are actively escalating.
    """)

    st.divider()

    # Get all amplitude watch entries
    amp_entries = get_amplitude_watch()

    if amp_entries:
        # Create summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            active = [e for e in amp_entries if e['status'] in ['ACCELERATING', 'STRUCTURAL']]
            st.metric("Active Escalations", len(active))

        with col2:
            avg_amp = sum(e['current_amplitude'] or 0 for e in amp_entries) / len(amp_entries) if amp_entries else 0
            st.metric("Average Amplitude", f"{avg_amp:.1f}")

        with col3:
            at_risk = [e for e in amp_entries if (e['current_amplitude'] or 0) > (e['risk_threshold'] or 100) * 0.7]
            st.metric("At-Risk Nodes", len(at_risk))

        with col4:
            high_conf = [e for e in amp_entries if e['confidence'] in ['HIGH', 'VERY HIGH']]
            st.metric("High Confidence", len(high_conf))

        st.divider()

        # Amplitude visualization
        st.subheader("📈 Current Amplitude Levels by Status")

        viz_data = []
        for e in amp_entries:
            if e['current_amplitude'] is not None:
                viz_data.append({
                    'Node': f"Node {e['node_id']}",
                    'Mechanism': e['node_name'],
                    'Current': e['current_amplitude'],
                    'Risk Threshold': e['risk_threshold'],
                    'Status': e['status']
                })

        if viz_data:
            viz_df = pd.DataFrame(viz_data)
            fig = px.bar(viz_df, x='Mechanism', y='Current',
                        color='Status',
                        color_discrete_map={
                            'ACCELERATING': '#d03b3b',
                            'STRUCTURAL': '#fab219',
                            'EMERGING': '#ec835a',
                            'MODERATE': '#199e70',
                            'MONITORING': '#666666'
                        },
                        title="Cascade Node Amplitude (Escalation Magnitude)")
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig)

        st.divider()

        # Detailed watch log entries
        st.subheader("🔍 Detailed Amplitude Watch Entries")

        # Group by status for better organization
        statuses = ['ACCELERATING', 'STRUCTURAL', 'EMERGING', 'MODERATE', 'MONITORING']

        for status in statuses:
            status_entries = [e for e in amp_entries if e['status'] == status]

            if status_entries:
                with st.expander(f"**{status}** ({len(status_entries)} mechanisms)", expanded=(status in ['ACCELERATING', 'STRUCTURAL'])):
                    for entry in status_entries:
                        col1, col2 = st.columns([2, 3])

                        with col1:
                            st.markdown(f"**Node {entry['node_id']}: {entry['node_name']}**")
                            st.metric("Current Amplitude", f"{entry['current_amplitude']:.0f}" if entry['current_amplitude'] else "—")
                            st.metric("Risk Threshold", f"{entry['risk_threshold']:.0f}" if entry['risk_threshold'] else "—")

                            # Progress bar showing amplitude vs risk threshold
                            if entry['current_amplitude'] and entry['risk_threshold']:
                                pct = min(100, int(entry['current_amplitude'] / entry['risk_threshold'] * 100))
                                st.progress(pct / 100, text=f"{pct}% of risk threshold")

                        with col2:
                            st.markdown(f"**Escalation**: {entry['escalation_rate']}")
                            st.markdown(f"**Confidence**: {entry['confidence']}")
                            st.markdown(f"**Measurement Basis**: {entry['measurement_basis']}")
                            st.markdown(f"**Breakpoint**: {entry['breakpoint']}")
                            if entry['evidence']:
                                st.markdown(f"**Evidence**: {entry['evidence']}")

        st.divider()

        # Amplitude trends over time
        st.subheader("Reference Point Amplitude Trend")
        ref_points = get_reference_points()

        if ref_points:
            df_ref = pd.DataFrame(ref_points)
            df_ref['date_recorded'] = pd.to_datetime(df_ref['date_recorded'])
            df_ref = df_ref[df_ref['metric_name'] == 'Amplitude'].sort_values('date_recorded')

            if not df_ref.empty:
                fig = px.line(df_ref, x='date_recorded', y='value',
                             markers=True, title="Amplitude Trend")
                fig.update_xaxes(title_text="Date")
                fig.update_yaxes(title_text="Amplitude Value")
                st.plotly_chart(fig)
    else:
        st.info("No amplitude data available yet")

# ============================================
# 5. CASCADING NODES VISUALIZING
# ============================================
def section_cascading_nodes():
    st.header("🔗 Cascading Nodes Visualizing")

    st.subheader("CASCADE Sequences")

    sequences = get_cascade_sequences()

    if sequences:
        seq_df = pd.DataFrame(sequences)
        seq_df = seq_df[['cascade_id', 'name', 'node_sequence', 'confidence']]
        seq_df.columns = ['ID', 'Name', 'Node Chain', 'Confidence']
        st.dataframe(seq_df, width='stretch', hide_index=True)

        st.divider()

        st.subheader("Node Activation Matrix")

        nodes = get_all_nodes()

        # Create activation matrix
        node_grid = []
        for node in nodes:
            signals_for_node = get_node_signals(node['node_id'])
            node_grid.append({
                'Node': f"Node {node['node_id']}",
                'Mechanism': node['name'],
                'Status': node['status'].upper(),
                'Signals': len(signals_for_node),
                'Amplitude': node['amplitude'],
                'Frequency': node['frequency']
            })

        if node_grid:
            grid_df = pd.DataFrame(node_grid)
            st.dataframe(grid_df, width='stretch', hide_index=True)

            # Visualization
            st.subheader("Node Activity Scatter")

            fig = px.scatter(grid_df, x='Amplitude', y='Frequency',
                           size='Signals', hover_name='Mechanism',
                           color='Amplitude',
                           color_continuous_scale='Reds',
                           title="Node Activation Landscape")
            st.plotly_chart(fig)
    else:
        st.info("No CASCADE sequences recorded yet")

# ============================================
# 6. SYSTEMATIC UNDERESTIMATION
# ============================================
def section_systematic_underestimation():
    st.header("⚠️ Systematic Underestimation")

    st.subheader("Definition")
    st.markdown("""
    A structural pattern where institutions, models, and frameworks systematically underestimate
    climate crisis severity, speed, and interconnectedness—not from bad data, but because
    measurement and policy instruments are calibrated for a world that no longer exists.
    """)

    # Summary metrics
    summary = get_underestimation_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Findings", summary['total_findings'])
    with col2:
        st.metric("Critical Gaps", summary['critical'])
    with col3:
        st.metric("Domains Affected", summary['unique_domains'])
    with col4:
        st.metric("Categories", summary['unique_categories'])

    st.divider()

    # Filter by domain
    domains = get_underestimation_domains()
    if domains:
        selected_domain = st.selectbox("Filter by Domain", ["All"] + domains)

        if selected_domain == "All":
            findings = get_all_underestimations()
        else:
            findings = get_all_underestimations(domain=selected_domain)

        if findings:
            # Organize by severity
            critical_findings = [f for f in findings if f['severity'] == 'critical']
            serious_findings = [f for f in findings if f['severity'] == 'serious']
            moderate_findings = [f for f in findings if f['severity'] == 'moderate']

            # Display critical findings
            if critical_findings:
                st.subheader("🔴 Critical Underestimations")
                for finding in critical_findings:
                    with st.container(border=True):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.markdown(f"**{finding['domain'].title()}** — {finding['category'].title()}")
                            st.markdown(finding['finding_text'])
                            if finding['underestimation_factor']:
                                st.caption(f"**Underestimation Factor:** {finding['underestimation_factor']}")
                            if finding['actual_vs_predicted']:
                                st.caption(f"**Actual vs Predicted:** {finding['actual_vs_predicted']}")
                            if finding['evidence_text']:
                                st.caption(f"**Evidence:** {finding['evidence_text']}")
                            st.caption(f"_Source: {finding['source']} | {finding['date_recorded'][:10]}_")
                        with col2:
                            st.markdown("<span style='color: #d03b3b; font-weight: 600; font-size: 12px;'>CRITICAL</span>", unsafe_allow_html=True)

            # Display serious findings
            if serious_findings:
                st.subheader("🟠 Serious Underestimations")
                for finding in serious_findings:
                    with st.container(border=True):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.markdown(f"**{finding['domain'].title()}** — {finding['category'].title()}")
                            st.markdown(finding['finding_text'])
                            if finding['underestimation_factor']:
                                st.caption(f"**Underestimation Factor:** {finding['underestimation_factor']}")
                            if finding['actual_vs_predicted']:
                                st.caption(f"**Actual vs Predicted:** {finding['actual_vs_predicted']}")
                            if finding['evidence_text']:
                                st.caption(f"**Evidence:** {finding['evidence_text']}")
                            st.caption(f"_Source: {finding['source']} | {finding['date_recorded'][:10]}_")
                        with col2:
                            st.markdown("<span style='color: #ec835a; font-weight: 600; font-size: 12px;'>SERIOUS</span>", unsafe_allow_html=True)

            # Display moderate findings
            if moderate_findings:
                with st.expander(f"🟡 Moderate Underestimations ({len(moderate_findings)})"):
                    for finding in moderate_findings:
                        with st.container(border=True):
                            st.markdown(f"**{finding['domain'].title()}** — {finding['category'].title()}")
                            st.markdown(finding['finding_text'])
                            if finding['underestimation_factor']:
                                st.caption(f"**Underestimation Factor:** {finding['underestimation_factor']}")
                            if finding['evidence_text']:
                                st.caption(f"**Evidence:** {finding['evidence_text']}")
                            st.caption(f"_Source: {finding['source']} | {finding['date_recorded'][:10]}_")

        else:
            st.info("No underestimation findings in this domain yet.")
    else:
        st.info("No systematic underestimation findings recorded yet.")

# ============================================
# 7. GRANULARITY
# ============================================
def section_granularity():
    st.header("🔬 Granularity")

    st.subheader("Signal Detail Breakdown")

    signals = get_all_signals()

    if signals:
        signals_df = pd.DataFrame(signals)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Signals", len(signals_df))
            st.metric("Unique Domains", signals_df['domain'].nunique())

        with col2:
            st.metric("Unique Severities", signals_df['severity'].nunique())
            st.metric("Unique Sources", signals_df['source'].nunique())

        with col3:
            active = signals_df[signals_df['status'] == 'active']
            st.metric("Active Signals", len(active))

        st.divider()

        st.subheader("Signals by Domain")

        domain_counts = signals_df['domain'].value_counts()
        fig = px.bar(x=domain_counts.index, y=domain_counts.values,
                    labels={'x': 'Domain', 'y': 'Signal Count'},
                    title="Signal Distribution by Domain")
        st.plotly_chart(fig)

        st.divider()

        st.subheader("Signals by Severity")

        severity_counts = signals_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index,
                    title="Severity Distribution")
        st.plotly_chart(fig)

        st.divider()

        st.subheader("All Signals (Detailed View)")
        st.dataframe(signals_df, width='stretch', hide_index=True)

    else:
        st.info("No signals recorded yet")

# ============================================
# 8. APPENDIX
# ============================================
def section_appendix():
    st.header("📚 Appendix")

    st.subheader("Baseline Return Failures")

    baseline_failures = get_baseline_failures()

    if baseline_failures:
        bf_df = pd.DataFrame(baseline_failures)
        bf_summary = bf_df.groupby('geography').agg({'baseline_shift_percent': 'first'}).reset_index()
        bf_summary.columns = ['Geography/Sector', 'Baseline Shift %']

        fig = px.bar(bf_summary, x='Geography/Sector', y='Baseline Shift %',
                    color='Baseline Shift %',
                    color_continuous_scale='Reds',
                    title="Baseline Return Failure by Geography")
        st.plotly_chart(fig)

        st.divider()

        st.subheader("Baseline Failure Details")
        st.dataframe(bf_df, width='stretch', hide_index=True)
    else:
        st.info("No baseline failure data recorded yet")

    st.divider()

    st.subheader("Data Schema")
    st.markdown("""
    **Project Cascade Database contains:**
    - **Cascade Nodes**: 13 primary mechanisms of system failure
    - **Signals**: Discrete observations of mechanism activation
    - **CASCADE Sequences**: Documented causal chains between nodes
    - **Reference Points**: Amplitude, Frequency, Interconnectedness, Underestimation
    - **Baseline Failures**: Geographic/sectoral baseline return patterns
    - **Daily Summaries**: Timestamped assessments and findings
    """)

# ============================================
# 9. SYSTEM MECHANISM TRACKER
# ============================================
def section_system_mechanism_tracker():
    st.header("🔬 System Mechanism Tracker")
    st.markdown("Distributed Adaptation Network & Baseline Return Failure Analysis")

    # Get data
    metrics = get_metrics_summary()
    nodes_by_activity = get_nodes_by_activity()
    cascades_with_signals = get_cascade_sequences_with_signals()
    hotspots = get_geographic_hotspots()
    amplitude_watch = get_amplitude_watch()

    # KEY METRICS ROW
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Signals", metrics['total_signals'], "+20 since Aug 17")
    with col2:
        active_count = len([n for n in nodes_by_activity if n['status'] == 'active'])
        st.metric("Active Mechanisms", f"{active_count}/13", "Nodes 3,4,5,6,7,11,13")
    with col3:
        st.metric("System Robustness", "−12%", "↓ −7% degradation")
    with col4:
        st.metric("CASCADE Sequences", metrics['cascade_sequences'], "5+ simultaneous")

    st.divider()

    # NODE ACTIVATION STATUS
    st.subheader("Node Activation Status — Amplitude & Frequency")

    # Create node cards with dynamic coloring
    node_map = {
        3: ("Institutional Suppression", "#d03b3b"),
        4: ("Rate of Change", "#d03b3b"),
        5: ("Thresholds Becoming Floors", "#d03b3b"),
        6: ("Measurement Erosion", "#ec835a"),
        7: ("Economic Depletion", "#d03b3b"),
        11: ("Infrastructure Lock-In", "#ec835a"),
        13: ("Change/Adaptation Lag", "#d03b3b"),
    }

    cols = st.columns(7)
    for idx, (node_id, (name, color)) in enumerate(node_map.items()):
        with cols[idx]:
            # Get node status from database
            node_data = next((n for n in nodes_by_activity if n['node_id'] == node_id), None)
            amplitude = f"{node_data['amplitude']:.1f}" if node_data else "—"

            # Find corresponding amplitude watch entry
            amp_watch = next((a for a in amplitude_watch if a['node_id'] == node_id), None)
            status = amp_watch['status'] if amp_watch else 'MONITORING'

            st.markdown(f"""
            <div style='background: #252423; border-left: 4px solid {color}; border-radius: 6px; padding: 16px; text-align: center;'>
                <div style='font-size: 12px; font-weight: 600; color: #c3c2b7; margin-bottom: 8px;'>Node {node_id}</div>
                <div style='font-size: 20px; font-weight: 600; color: #ffffff; margin-bottom: 4px;'>{status}</div>
                <div style='font-size: 11px; color: #8a8984;'>{name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # CHARTS SECTION
    st.subheader("Analysis & Trends")

    chart_col1, chart_col2 = st.columns(2)

    # Signal Distribution Chart
    with chart_col1:
        st.markdown("**Signal Distribution Across Nodes**")
        nodes_by_act = sorted(nodes_by_activity, key=lambda x: x['signal_count'], reverse=True)[:7]

        signal_data = {
            'Node': [f"Node {n['node_id']}" for n in nodes_by_act],
            'Signals': [n['signal_count'] for n in nodes_by_act]
        }

        fig = px.bar(
            signal_data,
            x='Node',
            y='Signals',
            color='Signals',
            color_continuous_scale=['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9'],
            labels={'Signals': 'Signal Count'},
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c3c2b7'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#383835'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig)

    # Reference Points Trend
    with chart_col2:
        st.markdown("**Reference Points Escalation**")

        ref_trend = {
            'Date': ['Aug 14', 'Aug 15', 'Aug 16', 'Aug 17', 'Aug 18'],
            'Amplitude': [28, 28, 28, 28, 34],
            'Frequency': [36, 36, 36, 36, 44],
            'Interconnectedness': [26, 26, 26, 26, 33],
        }

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ref_trend['Date'], y=ref_trend['Amplitude'],
                                name='Amplitude', line=dict(color='#3987e5', width=2)))
        fig.add_trace(go.Scatter(x=ref_trend['Date'], y=ref_trend['Frequency'],
                                name='Frequency', line=dict(color='#d95926', width=2)))
        fig.add_trace(go.Scatter(x=ref_trend['Date'], y=ref_trend['Interconnectedness'],
                                name='Interconnectedness', line=dict(color='#199e70', width=2)))

        fig.update_layout(
            height=300,
            hovermode='x unified',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c3c2b7'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#383835'),
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig)

    robustness_col, baseline_col = st.columns(2)

    # System Robustness
    with robustness_col:
        st.markdown("**System Robustness Degradation**")

        robustness_data = {
            'Date': ['Aug 14', 'Aug 15', 'Aug 16', 'Aug 17', 'Aug 18'],
            'Robustness': [-2, -3, -4, -5, -12],
        }

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=robustness_data['Date'],
            y=robustness_data['Robustness'],
            fill='tozeroy',
            line=dict(color='#d03b3b', width=3),
            fillcolor='rgba(208, 59, 59, 0.1)',
            name='System Robustness'
        ))

        fig.update_layout(
            height=300,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c3c2b7'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#383835', ticksuffix='%'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig)

    # Baseline Return Failures
    with baseline_col:
        st.markdown("**Baseline Return Failures — Geographic Expansion**")

        baseline_data = {
            'Region': ['Colorado River', 'Great Lakes', 'U.S. Agriculture', 'SE Asia', 'Sub-Saharan', 'Louisiana'],
            'Impact': ['−33%', '−18%', '−6M acres', '−27%', '−31%', '−12 insurers'],
            'Sector': ['Water', 'Water', 'Crop', 'Agr+Water', 'Agr+Water', 'Insurance']
        }

        for idx, region in enumerate(baseline_data['Region']):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"**{region}** — {baseline_data['Sector'][idx]}")
            with col2:
                st.caption(f"_{baseline_data['Impact'][idx]}_")

    st.divider()

    # CASCADE SEQUENCES
    st.subheader("Active CASCADE Sequences (5+ Simultaneous)")

    cascade_sequences = [
        ("CASCADE 4", "Node 7→6→10→3 (Economic Depletion Sequence)", "HIGH"),
        ("CASCADE 9", "Node 13→3 (Change Immunity Lock-In)", "HIGH"),
        ("CASCADE 10", "Node 3→7 (Institutional Suppression → Economic Depletion)", "HIGH"),
        ("CASCADE 11", "Node 3→6 (Institutional Suppression → Measurement Erosion)", "HIGH"),
        ("CASCADE 12", "Node 7→13 (Economic Depletion → Adaptation Lag)", "HIGH"),
    ]

    for name, nodes, conf in cascade_sequences:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"**{name}**")
        with col2:
            st.caption(nodes)
        with col3:
            st.markdown(f"<span style='background: #2f2e2c; padding: 4px 8px; border-radius: 4px; font-size: 11px; color: #d03b3b; font-weight: 600;'>{conf}</span>", unsafe_allow_html=True)

    st.divider()

    # KEY REFERENCE POINTS
    st.subheader("Key Reference Points — Amplitude, Frequency, Interconnectedness")

    ref_col1, ref_col2, ref_col3, ref_col4 = st.columns(4)

    ref_points = [
        ("Amplitude", 34, "+21%"),
        ("Frequency", 44, "+22%"),
        ("Interconnectedness", 33, "+27%"),
        ("Systematic Underestimation", 28, "+65%"),
    ]

    cols = [ref_col1, ref_col2, ref_col3, ref_col4]
    for idx, (label, value, delta) in enumerate(ref_points):
        with cols[idx]:
            st.markdown(f"""
            <div style='background: #2f2e2c; border-radius: 6px; padding: 12px; text-align: center;'>
                <div style='font-size: 11px; font-weight: 600; text-transform: uppercase; color: #c3c2b7; margin-bottom: 4px;'>{label}</div>
                <div style='font-size: 28px; font-weight: 600; color: #ffffff;'>{value}</div>
                <div style='font-size: 12px; color: #d03b3b; font-weight: 600;'>{delta} ↑</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.caption("Project Cascade — Distributed Adaptation Network & Baseline Return Failure Analysis Integrated | 17 Tracking Domains | Monthly Assessment Cycle")

# ============================================
# 10. PROJECT GOALS
# ============================================
def section_project_goals():
    st.header("🎯 Project Goals & Objectives")

    # Primary mission statement
    st.markdown("""
    ### Mission Statement
    Track and visualize forces and mechanisms that contribute to cascading failure and/or critical capacity
    thresholds across earth systems and human institutions.
    """)

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Active Goals", "Retired Goals", "Add New Goal"])

    all_goals = get_all_goals()
    active_goals = [g for g in all_goals if g['status'] == 'active']
    retired_goals = [g for g in all_goals if g['status'] == 'retired']

    # TAB 1: ACTIVE GOALS
    with tab1:
        st.subheader(f"Active Goals ({len(active_goals)})")

        if active_goals:
            for idx, goal in enumerate(active_goals):
                col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

                with col1:
                    st.markdown(f"""
                    <div style='background: #252423; border-left: 4px solid #199e70; border-radius: 6px; padding: 16px; margin: 8px 0;'>
                        <div style='font-size: 14px; color: #ffffff;'>{goal['goal_text']}</div>
                        <div style='font-size: 11px; color: #8a8984; margin-top: 8px;'>
                            Created: {goal['created_date'][:10]} | Category: {goal['category']}
                        </div>
                        {f"<div style='font-size: 11px; color: #c3c2b7; margin-top: 4px;'>Last amended: {goal['amended_date'][:10]}</div>" if goal['amended_date'] else ""}
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("✏️", key=f"edit_{goal['goal_id']}", help="Edit goal"):
                        st.session_state.edit_goal_id = goal['goal_id']

                with col3:
                    if st.button("🗑️", key=f"retire_{goal['goal_id']}", help="Retire goal"):
                        retire_goal(goal['goal_id'], f"Retired on {datetime.now().strftime('%Y-%m-%d')}")
                        st.rerun()

            # Edit mode
            if 'edit_goal_id' in st.session_state:
                goal_to_edit = next((g for g in active_goals if g['goal_id'] == st.session_state.edit_goal_id), None)
                if goal_to_edit:
                    st.divider()
                    st.subheader("Edit Goal")

                    edited_text = st.text_area("Goal Text", value=goal_to_edit['goal_text'], height=100)
                    edited_category = st.selectbox("Category",
                                                   ["primary", "secondary", "supporting", "monitoring"],
                                                   index=["primary", "secondary", "supporting", "monitoring"].index(goal_to_edit['category']))

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes"):
                            update_goal(st.session_state.edit_goal_id, edited_text, edited_category)
                            del st.session_state.edit_goal_id
                            st.success("Goal updated!")
                            st.rerun()

                    with col2:
                        if st.button("❌ Cancel"):
                            del st.session_state.edit_goal_id
                            st.rerun()
        else:
            st.info("No active goals yet. Add one using the 'Add New Goal' tab.")

    # TAB 2: RETIRED GOALS
    with tab2:
        st.subheader(f"Retired Goals ({len(retired_goals)})")

        if retired_goals:
            for goal in retired_goals:
                col1, col2 = st.columns([0.9, 0.1])

                with col1:
                    st.markdown(f"""
                    <div style='background: #252423; border-left: 4px solid #8a8984; border-radius: 6px; padding: 16px; margin: 8px 0; opacity: 0.7;'>
                        <div style='font-size: 14px; color: #c3c2b7;'>{goal['goal_text']}</div>
                        <div style='font-size: 11px; color: #8a8984; margin-top: 8px;'>
                            Retired: {goal['retired_date'][:10]} | {goal['notes']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("↩️", key=f"reactivate_{goal['goal_id']}", help="Reactivate goal"):
                        activate_goal(goal['goal_id'])
                        st.success("Goal reactivated!")
                        st.rerun()
        else:
            st.info("No retired goals.")

    # TAB 3: ADD NEW GOAL
    with tab3:
        st.subheader("Add New Goal")

        new_goal_text = st.text_area(
            "Goal Description",
            placeholder="Enter a new project goal...",
            height=100
        )

        new_category = st.selectbox(
            "Category",
            ["primary", "secondary", "supporting", "monitoring"]
        )

        if st.button("➕ Add Goal", type="primary"):
            if new_goal_text.strip():
                add_goal(new_goal_text, new_category)
                st.success("Goal added successfully!")
                st.rerun()
            else:
                st.error("Please enter a goal description.")

    st.divider()

    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Active Goals", len(active_goals))
    with col2:
        st.metric("Retired Goals", len(retired_goals))
    with col3:
        st.metric("Total Goals", len(all_goals))

# ============================================
# 9. RESEARCH FINDINGS
# ============================================
def section_findings():
    st.header("🔬 Research Findings — Mechanisms and Evidence")

    # Summary metrics
    findings_summary = get_findings_summary()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Findings", findings_summary['total_findings'])
    with col2:
        st.metric("Average Confidence", f"{findings_summary['avg_confidence']:.2%}")
    with col3:
        st.metric("Mechanisms Covered", findings_summary['unique_mechanisms'])

    st.markdown("---")

    # Mechanism breakdown
    st.subheader("📊 Findings by Mechanism")

    mechanisms_data = get_findings_by_mechanism()
    if mechanisms_data:
        # Create mechanism distribution chart
        mech_df = pd.DataFrame(mechanisms_data)

        col1, col2 = st.columns(2)

        # Chart 1: Findings count by mechanism
        with col1:
            fig_count = px.bar(
                mech_df,
                x='mechanism',
                y='count',
                title='Number of Findings per Mechanism',
                labels={'count': 'Finding Count', 'mechanism': 'Mechanism'},
                color='count',
                color_continuous_scale=['#3987e5', '#5a6fd8', '#7c57d1']
            )
            fig_count.update_layout(
                showlegend=False,
                height=400,
                font=dict(size=11)
            )
            st.plotly_chart(fig_count)

        # Chart 2: Average confidence by mechanism
        with col2:
            fig_conf = px.bar(
                mech_df,
                x='mechanism',
                y='avg_confidence',
                title='Average Confidence Level by Mechanism',
                labels={'avg_confidence': 'Avg Confidence', 'mechanism': 'Mechanism'},
                color='avg_confidence',
                color_continuous_scale=['#ec835a', '#fab219', '#87d03b']
            )
            fig_conf.update_layout(
                showlegend=False,
                height=400,
                font=dict(size=11),
                yaxis=dict(tickformat='.0%')
            )
            st.plotly_chart(fig_conf)

    st.markdown("---")

    # Detailed findings by mechanism
    st.subheader("📋 Findings Details")

    mechanisms = get_mechanisms_list()
    selected_mechanism = st.selectbox(
        "Filter by Mechanism",
        ["All Mechanisms"] + mechanisms,
        index=0
    )

    if selected_mechanism == "All Mechanisms":
        findings = get_all_findings()
    else:
        findings = get_all_findings(mechanism=selected_mechanism)

    if findings:
        # Group findings by confidence level for better visualization
        critical_conf = [f for f in findings if f['confidence_level'] >= 0.85]
        high_conf = [f for f in findings if 0.75 <= f['confidence_level'] < 0.85]
        moderate_conf = [f for f in findings if f['confidence_level'] < 0.75]

        # Display critical confidence findings
        if critical_conf:
            st.subheader("🟢 High Confidence (≥85%)")
            for finding in critical_conf:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{finding['mechanism']}**")
                        st.write(finding['finding_text'])
                    with col2:
                        st.metric("Confidence", f"{finding['confidence_level']:.0%}")
                    if finding['supporting_evidence']:
                        st.caption(f"📍 Evidence: {finding['supporting_evidence']}")
                    st.divider()

        # Display high confidence findings
        if high_conf:
            with st.expander(f"🟡 Moderate-High Confidence (75-85%)", expanded=False):
                for finding in high_conf:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{finding['mechanism']}**")
                        st.write(finding['finding_text'])
                    with col2:
                        st.metric("Confidence", f"{finding['confidence_level']:.0%}")
                    if finding['supporting_evidence']:
                        st.caption(f"📍 Evidence: {finding['supporting_evidence']}")
                    st.divider()

        # Display moderate confidence findings
        if moderate_conf:
            with st.expander(f"🔵 Emerging Findings (<75%)", expanded=False):
                for finding in moderate_conf:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{finding['mechanism']}**")
                        st.write(finding['finding_text'])
                    with col2:
                        st.metric("Confidence", f"{finding['confidence_level']:.0%}")
                    if finding['supporting_evidence']:
                        st.caption(f"📍 Evidence: {finding['supporting_evidence']}")
                    st.divider()
    else:
        st.info("No findings available for selected mechanism.")

    st.markdown("---")

    # Confidence distribution chart
    st.subheader("📈 Confidence Distribution")

    if findings:
        confidence_data = {
            'Critical (≥85%)': len(critical_conf),
            'High (75-85%)': len(high_conf),
            'Emerging (<75%)': len(moderate_conf)
        }

        fig_dist = go.Figure(data=[
            go.Pie(
                labels=list(confidence_data.keys()),
                values=list(confidence_data.values()),
                marker=dict(colors=['#87d03b', '#fab219', '#ec835a']),
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
            )
        ])

        fig_dist.update_layout(
            height=400,
            font=dict(size=12)
        )

        st.plotly_chart(fig_dist)

        # Timeline of discoveries
        st.subheader("📅 Findings Timeline")

        findings_sorted = sorted(findings, key=lambda x: x['date_discovered'])
        timeline_df = pd.DataFrame({
            'Date': [f['date_discovered'] for f in findings_sorted],
            'Mechanism': [f['mechanism'] for f in findings_sorted],
            'Confidence': [f['confidence_level'] for f in findings_sorted],
            'Finding': [f['finding_text'][:60] + '...' for f in findings_sorted]
        })

        fig_timeline = px.scatter(
            timeline_df,
            x='Date',
            y='Confidence',
            color='Mechanism',
            size=[1]*len(timeline_df),
            hover_data=['Finding'],
            title='Research Findings Discovery Timeline',
            height=400
        )

        fig_timeline.update_layout(
            hovermode='closest',
            font=dict(size=11),
            yaxis=dict(tickformat='.0%')
        )

        st.plotly_chart(fig_timeline)

# ============================================
# MAIN APP
# ============================================
def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("Project Cascade")
        st.markdown("---")

        sections = [
            "Summary",
            "Today's Progress",
            "System Mechanism Tracker",
            "Project Goals",
            "Mission and Goals",
            "Amplitude",
            "Cascading Nodes Visualizing",
            "Systematic Underestimation",
            "Findings",
            "Granularity",
            "Appendix"
        ]

        selected = st.radio("Navigation", sections, label_visibility="collapsed")

    # Main content
    if selected == "Summary":
        section_summary()
    elif selected == "Today's Progress":
        section_today_progress()
    elif selected == "System Mechanism Tracker":
        section_system_mechanism_tracker()
    elif selected == "Project Goals":
        section_project_goals()
    elif selected == "Mission and Goals":
        section_mission_goals()
    elif selected == "Amplitude":
        section_amplitude()
    elif selected == "Cascading Nodes Visualizing":
        section_cascading_nodes()
    elif selected == "Systematic Underestimation":
        section_systematic_underestimation()
    elif selected == "Findings":
        section_findings()
    elif selected == "Granularity":
        section_granularity()
    elif selected == "Appendix":
        section_appendix()

    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
