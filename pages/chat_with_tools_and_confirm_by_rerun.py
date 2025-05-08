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


st.title("💬 聊天机器人")
st.caption("🚀 由OpenAI LLM驱动的Streamlit聊天机器人")

with st.sidebar:
    show_history = st.checkbox('显示历史记录', False)
    reset_history = st.button("重置历史记录")

# 初始化会话状态
if "chat_history" not in st.session_state or reset_history:
    st.session_state["chat_history"] = [{"role": "assistant", "content": "有什么可以帮到您？"}]
    
# 初始化待确认的工具调用状态
if "pending_tool_calls" not in st.session_state or reset_history:
    st.session_state["pending_tool_calls"] = None

# 显示对话历史
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# 处理待确认的工具调用
if st.session_state.pending_tool_calls:
    with st.chat_message("assistant"):
        st.write("我需要使用工具来回答您的问题。请确认以下工具调用：")
        
        for tool_call in st.session_state.pending_tool_calls:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
            
            tool_info = f"**工具**: {function_name}"
            args_info = f"**参数**: {json.dumps(function_args, ensure_ascii=False, indent=2)}"
            
            st.info(f"{tool_info}\n\n{args_info}")
    
    # 显示确认和拒绝按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认调用", key="confirm_tool_call", type="primary"):
            # 执行工具调用
            tool_calls = st.session_state.pending_tool_calls
            st.session_state.chat_history.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
            
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                function_response = TOOL_HOOKS[function_name](**function_args)
                
                with st.chat_message("tool", avatar='🛠️'):
                    with st.status(f"调用工具: {function_name} 使用参数: {function_args}"):
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
            st.session_state.pending_tool_calls = None
            st.rerun()
    
    with col2:
        if st.button("拒绝调用", key="reject_tool_call"):
            st.session_state.chat_history.append({"role": "assistant", "content": "您拒绝了工具调用，我将尝试不使用工具来回答您的问题。"})
            st.session_state.pending_tool_calls = None
            st.rerun()

# 用户输入处理
elif prompt := st.chat_input():
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response_messages = ''
    response = chat_stream(st.session_state.chat_history, tools=tools)
    first_item = next(response)
    
    if isinstance(first_item, list):
        # 工具调用，等待用户确认
        tool_calls = first_item
        st.session_state.pending_tool_calls = tool_calls
        st.rerun()
    else:
        # 普通消息，直接显示
        with st.chat_message("assistant"):
            response_messages = st.write_stream(itertools.chain([first_item], response))
        st.session_state.chat_history.append({"role": "assistant", "content": response_messages})
    
if show_history:
    st.write(st.session_state.chat_history)
