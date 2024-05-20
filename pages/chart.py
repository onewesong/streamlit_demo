import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

tab_1, tab_2, tab_3, tab_4, tab_5, tab_6 = st.tabs(["base", "altair", "altair multi layer", "graphviz", "pyplot", "vega"])

with tab_1:
    with st.echo():
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    with st.echo():
        st.line_chart(chart_data)
    with st.echo():
        st.scatter_chart(chart_data)
    with st.echo():
        st.bar_chart(chart_data)
    with st.echo():
        st.area_chart(chart_data)
    
with tab_2:
    with st.echo():
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        c = (
            alt.Chart(chart_data)
            .mark_circle()
            .encode(x="a", y="b", size="c", color="c", tooltip=["a", "b", "c"])
        )
        st.altair_chart(c, use_container_width=True)

from vega_datasets import data

# We use @st.cache_data to keep the dataset in cache
@st.cache_data
def get_data():
    source = data.stocks()
    source = source[source.date.gt("2004-01-01")]
    return source

# Define the base time-series chart.
def get_chart(data):
    hover = alt.selection_single(
        fields=["date"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="Evolution of stock prices")
        .mark_line()
        .encode(
            x="date",
            y="price",
            color="symbol",
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="yearmonthdate(date)",
            y="price",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("date", title="Date"),
                alt.Tooltip("price", title="Price (USD)"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()


with tab_3:
    source = get_data()
    chart = get_chart(source)
    st.altair_chart(chart, use_container_width=True)

    with st.echo("below"):
        ANNOTATIONS = [
            ("Mar 01, 2008", "Pretty good day for GOOG"),
            ("Dec 01, 2007", "Something's going wrong for GOOG & AAPL"),
            ("Nov 01, 2008", "Market starts again thanks to..."),
            ("Dec 01, 2009", "Small crash for GOOG after..."),
        ]
        annotations_df = pd.DataFrame(ANNOTATIONS, columns=["date", "event"])
        annotations_df.date = pd.to_datetime(annotations_df.date)
        annotations_df["y"] = 10
        annotation_layer = (
            alt.Chart(annotations_df)
            .mark_text(size=20, text="⬇", dx=-8, dy=-10, align="left")
            .encode(
                x="date:T",
                y=alt.Y("y:Q"),
                tooltip=["event"],
            )
            .interactive()
        )
        st.altair_chart(
            (chart + annotation_layer).interactive(),
            use_container_width=True
        )

with tab_4:
    with st.echo():
        st.graphviz_chart('''
        digraph {
            run -> intr
            intr -> runbl
            runbl -> run
            run -> kernel
            kernel -> zombie
            kernel -> sleep
            kernel -> runmem
            sleep -> swap
            swap -> runswap
            runswap -> new
            runswap -> runmem
            new -> runmem
            sleep -> runmem
        }
    ''')

with tab_5:
    with st.echo():
        import matplotlib.pyplot as plt
        import numpy as np

        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        st.pyplot(fig)

with tab_6:
    with st.echo():
        source = data.cars()
        chart = {
            "mark": "point",
            "encoding": {
                "x": {
                    "field": "Horsepower",
                    "type": "quantitative",
                },
                "y": {
                    "field": "Miles_per_Gallon",
                    "type": "quantitative",
                },
                "color": {"field": "Origin", "type": "nominal"},
                "shape": {"field": "Origin", "type": "nominal"},
            },
        }
        st.vega_lite_chart(source, chart, theme="streamlit", use_container_width=True)
        st.write("source:", source)