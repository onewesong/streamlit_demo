import streamlit as st
from openai import OpenAI
import json
import itertools


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

def chat_stream(messages, model="gpt-4o-mini", tools=[], **kargs):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools if tools else None,
        stream=True,
        **kargs
    )
    tool_calls = []
    for chunk in response:
        if chunk and chunk.choices:
            delta = chunk.choices[0].delta
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
            elif delta.content:
                yield delta.content
    if tool_calls:
        yield tool_calls


st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

with st.sidebar:
    show_history = st.checkbox('Show history', False)
    reset_history = st.button("reset history")

if "chat_history" not in st.session_state or reset_history:
    st.session_state["chat_history"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state["pending_tool_calls"] = None
    st.session_state["tool_call_confirmed"] = False
    st.session_state["waiting_for_confirmation"] = False

for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# 定义插件确认界面函数
@st.fragment
def tool_confirmation():
    if st.session_state.waiting_for_confirmation and st.session_state.pending_tool_calls:
        tool_calls = st.session_state.pending_tool_calls
        
        with st.chat_message("assistant"):
            st.write("我需要调用以下插件，请确认是否继续：")
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                st.write(f"插件名称: {function_name}")
                st.write(f"参数: {function_args}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("确认执行"):
                    st.session_state.tool_call_confirmed = True
                    st.session_state.waiting_for_confirmation = False
                    st.rerun()
            with col2:
                if st.button("取消"):
                    st.session_state.pending_tool_calls = None
                    st.session_state.waiting_for_confirmation = False
                    st.session_state.chat_history.append({"role": "assistant", "content": "工具调用已取消。有什么我可以帮您的吗？"})
                    st.rerun(scope="fragment")

# 定义插件执行界面函数
@st.fragment
def tool_execution():
    if st.session_state.tool_call_confirmed and st.session_state.pending_tool_calls:
        tool_calls = st.session_state.pending_tool_calls
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
            stream = chat_stream(st.session_state.chat_history, tools=[])
            response_messages = st.write_stream(stream)
            st.session_state.chat_history.append({"role": "assistant", "content": response_messages})
        
        # 重置状态
        st.session_state.pending_tool_calls = None
        st.session_state.tool_call_confirmed = False

# 调用装饰器函数
tool_confirmation()
tool_execution()

if prompt := st.chat_input():
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    if not st.session_state.waiting_for_confirmation:
        response_messages = ''
        response = chat_stream(st.session_state.chat_history, tools=tools)
        first_item = next(response)
        
        if isinstance(first_item, list):
            # 发现工具调用，等待用户确认
            st.session_state.pending_tool_calls = first_item
            st.session_state.waiting_for_confirmation = True
            st.rerun()
        else:
            # 正常的文本响应
            with st.chat_message("assistant"):
                response_messages = st.write_stream(itertools.chain([first_item], response))
            st.session_state.chat_history.append({"role": "assistant", "content": response_messages})
    
if show_history:
    st.write(st.session_state.chat_history)
