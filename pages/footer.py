import streamlit as st

# 使用Markdown插入CSS
footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        color: black;
        text-align: center;
        padding: 10px;
    }
    </style>
    <div class="footer">
        <p>Created by Your Name © 2024</p>
    </div>
    """

# 在页面底部插入自定义的CSS和HTML
st.markdown(footer, unsafe_allow_html=True)

st.title('Streamlit App with Footer')
st.write("Your Streamlit app content goes here.")