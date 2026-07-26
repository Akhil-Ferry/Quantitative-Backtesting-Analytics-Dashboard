import streamlit as st
from config import APP_TITLE, APP_ICON, PAGE_CONFIG

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, **PAGE_CONFIG)

st.markdown("""
<style>
    .stApp header {background-color: transparent;}
    .main-title {text-align: center; padding: 1rem 0;}
    .main-title h1 {margin: 0; font-size: 2.2rem;}
    .main-title p {color: #888; font-size: 1rem; margin-top: 0.3rem;}
    section[data-testid="stSidebar"] {width: 260px !important;}
    .stMetric label {font-size: 0.85rem;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    f'<div class="main-title"><h1>{APP_ICON} {APP_TITLE}</h1>'
    f"<p>Backtest strategies · Analyze performance · Optimize parameters</p></div>",
    unsafe_allow_html=True,
)

if "data" not in st.session_state:
    st.session_state["data"] = None
if "data_source" not in st.session_state:
    st.session_state["data_source"] = None
if "backtest_triggered" not in st.session_state:
    st.session_state["backtest_triggered"] = False

pages = {
    "📊 Dashboard": "dashboard",
    "🎯 Backtest": "backtest",
    "📈 Analytics": "analytics",
    "⚖️ Comparison": "strategy_comparison",
}

with st.sidebar:
    st.markdown("### Navigation")
    selection = st.radio("Go to", list(pages.keys()), label_visibility="collapsed")

    st.divider()
    st.caption(f"Data: {st.session_state.get('data_source', 'None loaded')}")

    st.divider()
    st.caption("Built with Streamlit · Pandas · NumPy · Plotly")

page_module = pages[selection]
if page_module == "dashboard":
    from pages.dashboard import render
elif page_module == "backtest":
    from pages.backtest import render
elif page_module == "analytics":
    from pages.analytics import render
elif page_module == "strategy_comparison":
    from pages.strategy_comparison import render

render()
