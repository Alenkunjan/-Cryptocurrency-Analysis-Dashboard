import streamlit as st

st.set_page_config(page_title='Crypto Dashboard', page_icon='📊', layout='wide')

# Optional database initialization (kept for compatibility)
try:
    import database
    database.init_db()
except Exception:
    pass

# Immediately navigate to the dashboard page
st.switch_page('pages/dashboard.py')
