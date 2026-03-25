"""MCP Playground — entry point and page router."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="MCP Playground",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("pages/2_MCP_Concepts.py", title="How MCP Works", icon="📚"),
    st.Page("pages/mcp_playground.py", title="MCP Playground", icon="🔌", default=True),
    st.Page("pages/1_Before_vs_After.py", title="Before vs After", icon="⚖️"),
])
pg.run()
