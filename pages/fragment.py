import streamlit as st
import random

with st.sidebar:
    run_every = st.number_input("run_every", min_value=1, max_value=100, value=3)

@st.fragment(run_every=run_every)
def random_image():
    random_number = random.randint(0, 1000)
    url = f"https://picsum.photos/1000/1000?{random_number}"
    st.image(url)
    st.write(f"random image of {url}")


random_image()

