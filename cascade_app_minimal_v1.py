# -*- coding: utf-8 -*-
"""Minimal diagnostic version of Project Cascade app"""
import streamlit as st

st.set_page_config(page_title="Project Cascade", page_icon="📊", layout="wide")
st.title("Project Cascade - Diagnostic Mode")

st.write("Testing app framework...")

try:
    st.write("Streamlit loaded")

    from datetime import datetime
    st.write("datetime imported")

    from cascade_db import get_metrics_summary, get_nodes_by_activity
    st.write("cascade_db imported")

    metrics = get_metrics_summary()
    st.write(f"get_metrics_summary() returned: {type(metrics)}")
    if metrics:
        st.write(f"  - Total Signals: {metrics.get('total_signals', 'N/A')}")

    nodes = get_nodes_by_activity()
    st.write(f"get_nodes_by_activity() returned: {type(nodes)} with {len(nodes) if nodes else 0} items")

    st.success("All systems operational - ready to restore full dashboard")

except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.error(traceback.format_exc())
