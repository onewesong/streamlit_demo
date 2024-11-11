import streamlit as st

def chat_stream():
    response = "This is mock response for test."
    for word in response.split():
        yield word + " "
        import time
        time.sleep(0.3)


stream = chat_stream()
with st.chat_message("assistant"):
    response = ""
    contain = st.empty()
    for i in stream:
        response += i
        contain.write(f"{response}")

st.write(response)