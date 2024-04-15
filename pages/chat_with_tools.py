import streamlit as st

from openai import OpenAI
import json


client = OpenAI()

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]
TOOL_HOOKS = {
    "get_current_weather": get_current_weather,
}

def chat_stream(messages, model="gpt-3.5-turbo", **kargs):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        **kargs
    )
    for chunk in response:
        if chunk.choices:
            yield chunk.choices[0].delta.content or ""


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
    response_messages = ''

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.chat_history,
        tools=tools,
        stream=True,
        tool_choice="auto",
    )
    tool_calls = []
    for part in response:
        if not part or not part.choices:
            continue
        delta = part.choices[0].delta
        if delta.content:
            with st.chat_message("assistant"):
                response_messages = st.write(delta.content)
        if delta.tool_calls:
            tcchunklist = delta.tool_calls
            for tcchunk in tcchunklist:
                if len(tool_calls) <= tcchunk.index:
                    tool_calls.append({"id": "", "type": "function", "function": { "name": "", "arguments": "" } })
                tc = tool_calls[tcchunk.index]
                if tcchunk.id:
                    tc["id"] += tcchunk.id
                if tcchunk.function.name:
                    tc["function"]["name"] += tcchunk.function.name
                if tcchunk.function.arguments:
                    tc["function"]["arguments"] += tcchunk.function.arguments    
    if tool_calls:
        st.session_state.chat_history.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
            function_response = TOOL_HOOKS[function_name](**function_args)
            with st.chat_message("tool", avatar='🛠️'):
                with st.status(f"调用插件: {function_name} 使用参数: {function_args}"):
                    st.write(function_response)
            st.session_state.chat_history.append(
                {
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        with st.chat_message("assistant"):
            stream = chat_stream(st.session_state.chat_history)
            response_messages = st.write_stream(stream)
    st.session_state.chat_history.append({"role": "assistant", "content": response_messages})
    
if show_history:
    st.write(st.session_state.chat_history)
