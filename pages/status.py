import time
import streamlit as st
import streamlit_nested_layout

with st.status("Downloading data..."):
    with st.expander("More info"):
        st.write("Downloading data...")
    time.sleep(1)

st.button("Rerun")