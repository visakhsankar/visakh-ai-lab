import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Single_Agent.py", title="Single Agent", icon="🤖"),
    st.Page("pages/1_Multi_Agent.py",  title="Multi Agent",  icon="🤝"),
])
pg.run()
