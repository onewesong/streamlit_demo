import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(
    page_title="大语言模型价格对比",
    page_icon="💰",
    layout="wide"
)

# 标题
st.title("🤖 大语言模型价格和上下文窗口对比")

# 加载数据
@st.cache_data
def load_model_data():
    with open("data/model_prices_and_context_window.json", "r") as f:
        data = json.load(f)
    return data

model_data = load_model_data()

# 准备数据
def prepare_dataframe():
    models_info = []
    
    for model_name, model_info in model_data.items():
        # 跳过第一个样本规格
        if model_name == "sample_spec":
            continue
            
        # 只处理有价格信息的模型
        if "input_cost_per_token" in model_info and "output_cost_per_token" in model_info:
            input_cost = model_info.get("input_cost_per_token", 0)
            output_cost = model_info.get("output_cost_per_token", 0)
            max_input_tokens = model_info.get("max_input_tokens", model_info.get("max_tokens", 0))
            max_output_tokens = model_info.get("max_output_tokens", model_info.get("max_tokens", 0))
            
            # 添加提供商信息
            provider = model_info.get("litellm_provider", "未知")
            
            # 添加到列表
            models_info.append({
                "模型名称": model_name,
                "提供商": provider,
                "输入价格(每百万tokens)": input_cost * 1000000,  # 转换为每百万tokens的价格
                "输出价格(每百万tokens)": output_cost * 1000000,  # 转换为每百万tokens的价格
                "最大输入tokens": max_input_tokens,
                "最大输出tokens": max_output_tokens,
                "模式": model_info.get("mode", "未知")
            })
    
    return pd.DataFrame(models_info)

df = prepare_dataframe()

# 侧边栏过滤器
st.sidebar.header("过滤选项")

# 根据提供商过滤
providers = ["所有提供商"] + sorted(df["提供商"].unique().tolist())
selected_provider = st.sidebar.selectbox("选择提供商", providers)

# 根据模式过滤
modes = ["所有模式"] + sorted(df["模式"].unique().tolist())
selected_mode = st.sidebar.selectbox("选择模式", modes)

# 应用过滤
filtered_df = df.copy()
if selected_provider != "所有提供商":
    filtered_df = filtered_df[filtered_df["提供商"] == selected_provider]
if selected_mode != "所有模式":
    filtered_df = filtered_df[filtered_df["模式"] == selected_mode]

# 限制显示的模型数量
max_models_to_show = st.sidebar.slider("显示模型数量", 5, 50, 20)

# 按输入价格排序
sorted_df = filtered_df.sort_values(by="输入价格(每百万tokens)", ascending=False).head(max_models_to_show)

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("模型价格对比 (每百万tokens)")
    
    # 创建价格对比图表
    fig = go.Figure()
    
    # 添加输入价格柱状图
    fig.add_trace(go.Bar(
        x=sorted_df["模型名称"],
        y=sorted_df["输入价格(每百万tokens)"],
        name="输入价格",
        marker_color='lightblue'
    ))
    
    # 添加输出价格柱状图
    fig.add_trace(go.Bar(
        x=sorted_df["模型名称"],
        y=sorted_df["输出价格(每百万tokens)"],
        name="输出价格",
        marker_color='lightgreen'
    ))
    
    # 更新布局
    fig.update_layout(
        barmode='group',
        xaxis_tickangle=-45,
        height=600,
        margin=dict(l=20, r=20, t=30, b=150),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("模型上下文窗口大小对比")
    
    # 创建上下文窗口大小对比图表
    fig2 = go.Figure()
    
    # 添加最大输入tokens柱状图
    fig2.add_trace(go.Bar(
        x=sorted_df["模型名称"],
        y=sorted_df["最大输入tokens"],
        name="最大输入tokens",
        marker_color='coral'
    ))
    
    # 添加最大输出tokens柱状图
    fig2.add_trace(go.Bar(
        x=sorted_df["模型名称"],
        y=sorted_df["最大输出tokens"],
        name="最大输出tokens",
        marker_color='mediumorchid'
    ))
    
    # 更新布局
    fig2.update_layout(
        barmode='group',
        xaxis_tickangle=-45,
        height=600,
        margin=dict(l=20, r=20, t=30, b=150),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# 显示模型价格表格
st.subheader("模型价格数据表")

# 添加搜索框
search_term = st.text_input("搜索模型名称")

# 根据搜索词过滤
if search_term:
    display_df = filtered_df[filtered_df["模型名称"].str.contains(search_term, case=False)]
else:
    display_df = filtered_df

# 排序并显示表格
display_df = display_df.sort_values(by="输入价格(每百万tokens)", ascending=False)
st.dataframe(display_df, use_container_width=True)

# 额外的分析部分
st.subheader("价格与上下文窗口关系分析")

# 创建一个散点图，展示价格与上下文窗口大小的关系
scatter_fig = px.scatter(
    filtered_df,
    x="最大输入tokens",
    y="输入价格(每百万tokens)",
    color="提供商",
    size="最大输出tokens",
    hover_name="模型名称",
    log_x=True,
    log_y=True,
    title="模型价格与上下文窗口大小的关系"
)

scatter_fig.update_layout(height=600)
st.plotly_chart(scatter_fig, use_container_width=True)

# 添加页脚
st.markdown("---")
st.markdown("📊 数据来源: model_prices_and_context_window.json")
st.markdown("�� 最后更新日期: 2024年8月")