from modules import *

from pyecharts import options as opts
from pyecharts.charts import Pie, Line, Bar, Timeline, Map
from pyecharts.faker import Faker
from streamlit_echarts import st_pyecharts

tab_pie, tab_line, tab_bar, tab_map, tab_timeline = st.tabs(["Pie", "Line", "Bar", "Map", "Timeline"])

with tab_pie:
    with st.echo():
        c = (
            Pie()
            .add("", [list(z) for z in zip(Faker.choose(), Faker.values())])
            .set_colors(["blue", "green", "yellow", "red", "pink", "orange", "purple"])
            .set_global_opts(title_opts=opts.TitleOpts(title="Pie-设置颜色"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )
        st_pyecharts(c)

        
with tab_line:
    with st.echo():
        l = (
            Line()
            .add_xaxis(Faker.choose())
            .add_yaxis("商家A", Faker.values())
            .add_yaxis("商家B", Faker.values())
            .set_global_opts(title_opts=opts.TitleOpts(title="Line-基本示例"))
        )
        st_pyecharts(l)

with tab_bar:
    with st.echo():
        b = (
            Bar()
            .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
            .add_yaxis(
                "2017-2018 Revenue in (billion $)", [21.2, 20.4, 10.3, 6.08, 4, 2.2]
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
                ),
                toolbox_opts=opts.ToolboxOpts(),
            )
        )
        st_pyecharts(b)


with tab_map:
    with st.echo():
        m = (
            Map()
            .add("商家A", [list(z) for z in zip(Faker.provinces, Faker.values())], "china")
            .set_global_opts(title_opts=opts.TitleOpts(title="Map-基本示例"))
        )
        st_pyecharts(m)


with tab_timeline:
    with st.echo():
        tl = Timeline()
        for i in range(2015, 2020):
            pie = (
                Pie()
                .add(
                    "商家A",
                    [list(z) for z in zip(Faker.choose(), Faker.values())],
                    rosetype="radius",
                    radius=["30%", "55%"],
                )
                .set_global_opts(title_opts=opts.TitleOpts("某商店{}年营业额".format(i)))
            )
            tl.add(pie, "{}年".format(i))

        st_pyecharts(tl, theme="dark", width="100%", height="300px")