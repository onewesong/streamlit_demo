import streamlit as st

def set_global_exception_handler(f):
    import sys
    error_util = sys.modules['streamlit.error_util']
    error_util.handle_uncaught_app_exception.__code__ = f.__code__

def exception_handler(e):
    # Custom error handling
    import streamlit as st
    st.image("https://media1.tenor.com/m/t7_iTN0iYekAAAAd/sad-sad-cat.gif")
    st.error(f"Oops, something funny happened with a {type(e).__name__}", icon="😿")

set_global_exception_handler(exception_handler)

st.title("Type issue")

raise TypeError("You put in the wrong type")