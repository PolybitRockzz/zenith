import streamlit as st

# Title of the app
st.set_page_config(page_title="Zenith AI Hedge Fund", page_icon="🤖", layout="wide")

# Create a multipage app using Streamlit's new multipage support
st.markdown("<p style='margin-bottom: 0px; padding-bottom: 0px;'>Zenith - AI Hedge Fund 🤖💹</p>", unsafe_allow_html=True)

# Define pages using st.navigation and st.Page with titles and icons
pg = st.navigation([
    st.Page("routes/home.py", title="Home", icon=":material/home:"),
    st.Page("routes/market-analysis.py", title="Market Analysis", icon=":material/bar_chart:"),
    st.Page("routes/trading-decisions.py", title="Trading Decisions", icon=":material/trending_up:"),
    st.Page("routes/about.py", title="About", icon=":material/info:")
])
pg.run()