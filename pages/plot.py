import pandas as pd
import streamlit as st

# 创建数据
data = {
    "log_date": ["2024-08-22", "2024-08-22", "2024-08-22", 
                 "2024-08-23", "2024-08-23", "2024-08-23", 
                 "2024-08-24"],
    "model_name": ["gpt-4o", "gpt-4o-mini", "codegeex4", 
                   "codegeex4", "gpt-4o-mini", "gpt-4o", 
                   "codegeex4"],
    "call_count": [21, 14, 8, 124, 65, 21, 12]
}

# 将数据转换为 DataFrame
df = pd.DataFrame(data)

# 将数据整理为适合绘图的格式
df_pivot = df.pivot(index='log_date', columns='model_name', values='call_count')

# 使用 Streamlit 绘制折线图
st.line_chart(df_pivot)

