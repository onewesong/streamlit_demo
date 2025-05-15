import streamlit as st
import time
st.title("Streamlit Extras Demo", help="https://arnaudmiribel.github.io/streamlit-extras/")

tabs = st.tabs(["Chart", "Grid", "Other"])

with tabs[0]:
    with st.echo("below"):
        from streamlit_extras.chart_container import chart_container, get_random_data
        chart_data = get_random_data()
        with chart_container(chart_data):
            st.write("Here's a cool chart")
            st.area_chart(chart_data)

with tabs[1]:
    with st.echo("below"):
        from streamlit_extras.grid import grid, example
        example()
        
with tabs[2]:
    with st.echo("below"):
        from streamlit_extras.badges import badge
        badge(type="streamlit", url="https://plost.streamlitapp.com")
        badge(type="github", name="streamlit/streamlit")
    with st.echo("below"):
        from streamlit_extras.keyboard_url import keyboard_to_url, load_key_css, key
        keyboard_to_url(key="S", url="https://www.github.com/streamlit/streamlit")

        load_key_css()
        st.write(
            f"""Now hit {key("S", False)} on your keyboard...!""",
            unsafe_allow_html=True,
        )
    with st.echo("below"):
        from streamlit_extras.stoggle import stoggle
        stoggle(
            "Click me!",
            """🥷 Surprise! Here's some additional content""",
        )

    with st.echo("below"):
        from streamlit_extras.tags import tagger_component
        tagger_component("Here is a feature request", ["p2", "🚩triaged", "backlog"])
        tagger_component(
            "Here are colored tags",
            ["turtle", "rabbit", "lion"],
            color_name=["blue", "orange", "lightblue"],
        )
        tagger_component(
            "Annotate the feature",
            ["hallucination"],
            color_name=["blue"],
        )
