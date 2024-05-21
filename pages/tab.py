import streamlit as st

tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    st.write("This is the first tab")
    tab11, tab12 = st.tabs(["Tab 1.1", "Tab 1.2"])
    with tab11:
        st.write("This is the first sub-tab of the first tab")
    with tab12:
        st.write("This is the second sub-tab of the first tab")