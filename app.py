import streamlit as st


st.set_page_config(
    page_title="Dashboard BI - MBG Indonesia 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    [data-testid="metric-container"] {
        background-color: #f0f4ff;
        border: 1px solid #d0d9f0;
        border-radius: 10px;
        padding: 12px 16px;
    }
    .block-container { padding-top: 1.5rem; }
</style>
""",
    unsafe_allow_html=True,
)

pages = [
    ("pages/1_Nasional.py", "Dashboard Nasional"),
    ("pages/2_Provinsi.py", "Lihat Detail Provinsi"),
]

if hasattr(st, "Page") and hasattr(st, "navigation"):
    pg = st.navigation([st.Page(path, title=title) for path, title in pages])
    pg.run()
else:
    st.title("Dashboard BI - MBG Indonesia 2026")
    st.error(
        "This app needs Streamlit 1.36 or newer for st.Page/st.navigation. "
        "Upgrade it with: pip install --upgrade streamlit"
    )
