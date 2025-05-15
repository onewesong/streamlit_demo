from streamlit_extras.let_it_rain import rain
import streamlit as st
emoji = st.text_input("Enter an emoji")
font_size = st.slider("Font size", min_value=10, max_value=200, value=54)
falling_speed = st.slider("Falling speed", min_value=1, max_value=10, value=5)

with st.echo("below"):
    rain(
        emoji=emoji or "🎈", 
        font_size=font_size,
        falling_speed=falling_speed,
        animation_length="infinite",
    )