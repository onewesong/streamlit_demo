import streamlit as st
import time

import streamlit as st

placeholder = st.empty()
time.sleep(2)

# Replace the placeholder with some text:
placeholder.text("Hello")
time.sleep(2)

# Replace the text with a chart:
placeholder.line_chart({"data": [1, 5, 2, 6]})
time.sleep(2)

# Replace the chart with several elements:
with placeholder.container():
    st.write("This is one element")
    st.write("This is another")

time.sleep(2)
# Clear all those elements:
placeholder.empty()