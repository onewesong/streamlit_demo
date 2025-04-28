import streamlit as st
import streamlit.components.v1 as components

# embed streamlit docs in a streamlit app
components.iframe("https://example.com", height=500)

# 内部路由
components.iframe("/chat", height=500)

