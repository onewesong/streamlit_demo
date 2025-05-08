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

def chat_stream(messages, model="gpt-3.5-turbo", tools=[], **kargs):
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

# 回调函数：确认工具调用
def confirm_tool_call():
    tool_calls = st.session_state.pending_tool_calls
    
    # 将工具调用添加到聊天历史
    st.session_state.chat_history.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
    
    # 执行每个工具调用并存储结果
    for tool_call in tool_calls:
        function_name = tool_call["function"]["name"]
        function_args = json.loads(tool_call["function"]["arguments"])
        function_response = TOOL_HOOKS[function_name](**function_args)
        
        # 存储工具调用结果
        st.session_state.tool_responses.append({
            "tool_call_id": tool_call["id"],
            "function_name": function_name,
            "function_args": function_args,
            "function_response": function_response
        })
        
        # 将工具响应添加到聊天历史
        st.session_state.chat_history.append({
            "tool_call_id": tool_call["id"],
            "role": "tool",
            "name": function_name,
            "content": function_response,
        })
    
    # 标记需要获取AI的后续响应
    st.session_state.need_ai_response = True
    # 清除待确认的工具调用
    st.session_state.pending_tool_calls = None

# 回调函数：拒绝工具调用
def reject_tool_call():
    st.session_state.chat_history.append({"role": "assistant", "content": "您拒绝了工具调用，我将尝试不使用工具来回答您的问题。"})
    st.session_state.pending_tool_calls = None
    # 不需要获取AI的后续响应
    st.session_state.need_ai_response = False

# 初始化会话状态
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [{"role": "assistant", "content": "How can I help you?"}]
    
# 初始化待确认的工具调用状态
if "pending_tool_calls" not in st.session_state:
    st.session_state["pending_tool_calls"] = None

# 初始化工具响应状态
if "tool_responses" not in st.session_state:
    st.session_state["tool_responses"] = []

# 初始化是否需要AI响应的状态
if "need_ai_response" not in st.session_state:
    st.session_state["need_ai_response"] = False

# 初始化是否有新消息状态
if "has_new_message" not in st.session_state:
    st.session_state["has_new_message"] = False

# 页面标题
st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

# 侧边栏
with st.sidebar:
    show_history = st.checkbox('Show history', False)
    if st.button("Reset history"):
        st.session_state.chat_history = [{"role": "assistant", "content": "How can I help you?"}]
        st.session_state.pending_tool_calls = None
        st.session_state.tool_responses = []
        st.session_state.need_ai_response = False
        st.session_state.has_new_message = False

# 显示对话历史
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# 用户输入处理
if prompt := st.chat_input():
    st.session_state.has_new_message = True
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

# 如果有新消息且没有待处理的工具调用，则获取AI响应
if st.session_state.has_new_message and not st.session_state.pending_tool_calls:
    # 获取AI响应
    response = chat_stream(st.session_state.chat_history, tools=tools)
    first_item = next(response)
    
    if isinstance(first_item, list):
        # 工具调用，存储以待确认
        st.session_state.pending_tool_calls = first_item
    else:
        # 普通消息，直接显示
        with st.chat_message("assistant"):
            response_messages = st.write_stream(itertools.chain([first_item], response))
        st.session_state.chat_history.append({"role": "assistant", "content": response_messages})
    
    # 重置新消息标志
    st.session_state.has_new_message = False

# 显示工具调用的结果（如果有）
if st.session_state.tool_responses:
    # 显示最新一轮的工具响应
    for tool_response in st.session_state.tool_responses:
        with st.chat_message("tool", avatar='🛠️'):
            with st.status(f"调用工具: {tool_response['function_name']} 使用参数: {tool_response['function_args']}"):
                st.write(tool_response['function_response'])
    
    # 清除已显示的工具响应
    st.session_state.tool_responses = []

# 获取AI的后续响应（如果需要）
if st.session_state.need_ai_response:
    with st.chat_message("assistant"):
        stream = chat_stream(st.session_state.chat_history, tools=[])
        response_messages = st.write_stream(stream)
    
    # 添加AI响应到聊天历史
    st.session_state.chat_history.append({"role": "assistant", "content": response_messages})
    # 重置状态
    st.session_state.need_ai_response = False

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
        st.button("确认调用", key="confirm_tool_call", type="primary", on_click=confirm_tool_call)
    
    with col2:
        st.button("拒绝调用", key="reject_tool_call", on_click=reject_tool_call)

if show_history:
    st.write(st.session_state.chat_history)
