import streamlit as st

st.set_page_config(
    page_title="Dashboard BI - MBG Indonesia 2026",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
[data-testid="metric-container"] {
    background-color: #1e2a3a;
    border: 1px solid #2e4060;
    border-radius: 10px;
    padding: 14px 18px;
}
.block-container { padding-top: 1.5rem; }
</style>
""",
    unsafe_allow_html=True,
)

pages = [
    st.Page("pages/dashboard.py", title="Dashboard MBG Nasional 2026", icon="🍽️"),
]
pg = st.navigation(pages)
pg.run()
