import streamlit as st


if selected := st.feedback("stars", ):
    st.write(f"You selected {selected}")

if selected := st.feedback("faces", ):
    st.write(f"You selected {selected}")


selected = st.feedback("thumbs", )
if selected:
    st.write("You selected thumbs up!") 