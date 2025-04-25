import streamlit as st
import time

def chat_stream():
    response = "This is mock response for test."
    think_response = "I am thinking..."
    for word in think_response.split():
        yield {"resonning_content": word + " "}
        time.sleep(0.3)
    for word in response.split():
        yield word + " "
        time.sleep(0.3)

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

with st.sidebar:
    show_history = st.checkbox('Show history', False)
    reset_history = st.button("reset history")

if "chat_history" not in st.session_state or reset_history:
    st.session_state["chat_history"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        reasoning_content = ""
        stream = chat_stream()
        
        if isinstance(stream, dict):
            if 'reasoning_content' in stream:
                st.write(stream['reasoning_content'])
        else:
            response = st.write_stream(stream)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
if show_history:
    st.write(st.session_state.chat_history)
