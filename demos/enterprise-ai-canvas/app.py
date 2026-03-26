"""Enterprise AI Canvas — entry point."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st

st.set_page_config(
    page_title="Enterprise AI Canvas",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("pages/canvas.py", title="Capability Canvas", icon="🏗️", default=True),
    st.Page("pages/2_Capability_Library.py", title="Capability Library", icon="📦"),
])
pg.run()
