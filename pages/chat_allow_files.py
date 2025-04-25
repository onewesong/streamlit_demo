import streamlit as st

prompt = st.chat_input(
    "Say something and/or attach an image",
    accept_file="multiple",
    file_type=["jpg", "jpeg", "png", "pdf", "docx", "doc", "xls", "xlsx", "ppt", "pptx", "csv"],
)
if prompt and prompt.text:
    st.markdown(prompt.text)
if prompt and prompt["files"]:
    for file in prompt["files"]:
        if file.type.startswith('image/'):
            st.image(file)
        else:
            st.write(f"文件名: {file.name}")
            st.write(f"文件类型: {file.type}")
            st.write(f"文件大小: {file.size} bytes")