# -*- coding: utf-8 -*-
"""Minimal diagnostic version of Project Cascade app"""
import streamlit as st

st.set_page_config(page_title="Project Cascade", page_icon="[CHART]", layout="wide")
st.title("Project Cascade - Diagnostic Mode")

st.write("Testing app framework...")

try:
    st.write("[YES] Streamlit loaded")

    from datetime import datetime
    st.write("[YES] datetime imported")

    from cascade_db import get_metrics_summary, get_nodes_by_activity
    st.write("[YES] cascade_db imported")

    metrics = get_metrics_summary()
    st.write(f"[YES] get_metrics_summary() returned: {type(metrics)}")
    if metrics:
        st.write(f"  - Total Signals: {metrics.get('total_signals', 'N/A')}")

    nodes = get_nodes_by_activity()
    st.write(f"[YES] get_nodes_by_activity() returned: {type(nodes)} with {len(nodes) if nodes else 0} items")

    st.success("[YES] All systems operational - ready to restore full dashboard")

except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.error(traceback.format_exc())
