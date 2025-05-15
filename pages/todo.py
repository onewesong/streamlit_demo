import streamlit as st
from streamlit_extras.stodo import to_do

with st.echo("below"):
    to_do(
        [(st.write, "☕ Take my coffee")],
        "coffee",
    )
    to_do(
        [(st.write, "🥞 Have a nice breakfast")],
        "pancakes",
    )
    to_do(
        [(st.write, ":train: Go to work!")],
        "work",
    )
