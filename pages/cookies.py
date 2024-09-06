import streamlit as st
from streamlit_cookies_manager import CookieManager
cookies = CookieManager()

st.context.cookies

# Get cookies
if not cookies.ready():
    st.stop()
st.write("Current cookies:", cookies)

# Write cookies
cookies["a-cookie"] = "aaaa-value"
cookies.save()

st.context.cookies
