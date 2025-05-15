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

for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

@st.dialog(title="调用工具确认")
def tool_confirmation_dialog(tool_id_for_dialog: str, function_name: str, function_args_dict: dict):
    """
    显示工具调用确认对话框。
    用户点击按钮后，会更新 session_state 并触发 st.rerun()。
    """
    st.write(f"请确认是否执行以下工具调用：")
    st.markdown(f"**插件名称:** `{function_name}`")
    st.markdown(f"**参数:**")
    st.json(function_args_dict)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("确认执行", key=f"confirm_btn_{tool_id_for_dialog}", type="primary"):
            st.session_state.dialog_outcomes[tool_id_for_dialog] = True
            st.rerun()
    with col2:
        if st.button("拒绝执行", key=f"deny_btn_{tool_id_for_dialog}"):
            st.session_state.dialog_outcomes[tool_id_for_dialog] = False
            st.rerun()

# Initialize session state variables for tool call processing
if "tool_call_queue" not in st.session_state:
    st.session_state.tool_call_queue = []
if "tool_responses" not in st.session_state:
    st.session_state.tool_responses = []
if "dialog_outcomes" not in st.session_state: # Stores True/False for tool_id
    st.session_state.dialog_outcomes = {}
if "current_tool_for_confirmation" not in st.session_state: # Stores the tool_call object being confirmed
    st.session_state.current_tool_for_confirmation = None

if prompt := st.chat_input():
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Reset tool processing states for a new user prompt
    st.session_state.tool_call_queue = []
    st.session_state.tool_responses = []
    # Keep dialog_outcomes and current_tool_for_confirmation if a dialog might be open from a previous step,
    # though typically a new prompt implies starting fresh. For robustness with multi-turn tools,
    # a more sophisticated state management might be needed. Here, we reset them.
    st.session_state.dialog_outcomes = {}
    st.session_state.current_tool_for_confirmation = None

    response_stream = chat_stream(st.session_state.chat_history, tools=tools)
    
    # Eagerly consume the first item to check its type
    try:
        first_chunk = next(response_stream)
    except StopIteration:
        first_chunk = None # Stream was empty

    if isinstance(first_chunk, list): # LLM wants to call tools
        tool_calls = first_chunk
        # Add assistant message that intends to call tools
        # Content is None for now, will be filled by LLM after tool execution
        st.session_state.chat_history.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
        st.session_state.tool_call_queue.extend(tool_calls)
        st.rerun() # Rerun to start processing the tool_call_queue
    elif first_chunk is not None: # Normal text response
        with st.chat_message("assistant"):
            # Reconstruct the full stream for st.write_stream
            full_response_content = st.write_stream(itertools.chain([first_chunk], response_stream))
        st.session_state.chat_history.append({"role": "assistant", "content": full_response_content})
        # No rerun needed here, response is displayed.
    else:
        # Handle empty stream if necessary (e.g., LLM returned nothing)
        with st.chat_message("assistant"):
            st.write("我没有收到任何回复。")
        st.session_state.chat_history.append({"role": "assistant", "content": "我没有收到任何回复。"})


# --- Tool processing logic ---
# This block runs on every rerun if there are tools in the queue or one being confirmed.

if not st.session_state.current_tool_for_confirmation and st.session_state.tool_call_queue:
    # Pick the next tool to confirm from the queue
    st.session_state.current_tool_for_confirmation = st.session_state.tool_call_queue.pop(0)
    # Clear any old outcome for this tool_id in case of re-confirmation (though unlikely in this flow)
    if st.session_state.current_tool_for_confirmation['id'] in st.session_state.dialog_outcomes:
        del st.session_state.dialog_outcomes[st.session_state.current_tool_for_confirmation['id']]
    st.rerun() # Rerun to process the newly selected tool for confirmation

if st.session_state.current_tool_for_confirmation:
    tool_to_confirm = st.session_state.current_tool_for_confirmation
    tool_id = tool_to_confirm['id']
    function_name = tool_to_confirm["function"]["name"]
    
    try:
        function_args = json.loads(tool_to_confirm["function"]["arguments"])
    except json.JSONDecodeError:
        st.error(f"无法解析工具 {function_name} 的参数: {tool_to_confirm['function']['arguments']}")
        st.session_state.tool_responses.append({
            "tool_call_id": tool_id, "role": "tool", "name": function_name,
            "content": f"Error: Invalid arguments format for tool {function_name}."
        })
        st.session_state.current_tool_for_confirmation = None # Move to next or finish
        st.rerun()

    decision = st.session_state.dialog_outcomes.get(tool_id)

    if decision is None:
        # No decision yet, show the dialog.
        tool_confirmation_dialog(tool_id, function_name, function_args)
        # The script execution will end here. User interaction with the dialog will set
        # st.session_state.dialog_outcomes[tool_id] and trigger st.rerun().
        # On the next rerun, 'decision' will be populated.
    elif decision is True: # User confirmed
        # Displaying the tool execution status
        with st.chat_message("tool", avatar='🛠️'):
            status_message = f"调用插件: {function_name}"
            with st.status(status_message, expanded=True) as status_el:
                st.write(f"正在执行 {function_name}...")
                st.write(f"参数: {function_args}")
                try:
                    function_response_content = TOOL_HOOKS[function_name](**function_args)
                    st.write("执行成功!")
                    st.write("结果:")
                    try:
                        # Try to parse if it's a JSON string for pretty printing
                        parsed_res = json.loads(function_response_content)
                        st.json(parsed_res)
                    except (json.JSONDecodeError, TypeError):
                        st.write(function_response_content) # Otherwise, write as is
                    status_el.update(label=f"插件 {function_name} 执行完毕", state="complete")
                except Exception as e:
                    function_response_content = f"工具 {function_name} 执行错误: {str(e)}"
                    st.error(function_response_content) # Show error inside status too
                    status_el.update(label=f"插件 {function_name} 执行失败: {str(e)}", state="error")
        
        st.session_state.tool_responses.append({
            "tool_call_id": tool_id, "role": "tool", "name": function_name, "content": function_response_content
        })
        st.session_state.current_tool_for_confirmation = None # Done with this one
        st.rerun() # Rerun to process next in queue or finalize

    elif decision is False: # User denied
        st.warning(f"用户已拒绝执行工具: {function_name}")
        function_response_content = f"User denied tool call for {function_name}."
        st.session_state.tool_responses.append({
            "tool_call_id": tool_id, "role": "tool", "name": function_name, "content": function_response_content
        })
        st.session_state.current_tool_for_confirmation = None # Done with this one
        st.rerun() # Rerun to process next in queue or finalize

# After all tools in queue are processed and no tool is currently being confirmed
if not st.session_state.tool_call_queue and \
   not st.session_state.current_tool_for_confirmation and \
   st.session_state.tool_responses:
    
    # Ensure all tool responses are in the main chat history before calling LLM
    for resp in st.session_state.tool_responses:
        # Check if this exact response (by tool_call_id and role) is already in history to prevent duplicates
        is_already_added = any(
            h.get("tool_call_id") == resp["tool_call_id"] and h.get("role") == "tool" 
            for h in st.session_state.chat_history
        )
        if not is_already_added:
            st.session_state.chat_history.append(resp)

    with st.chat_message("assistant"):
        # Filter relevant history for the LLM. The history should now contain:
        # ..., user_prompt, assistant_message_with_tool_calls, tool_response_1, tool_response_2, ...
        stream_after_tools = chat_stream(st.session_state.chat_history, tools=[]) # No tools for this follow-up call
        final_response_content = st.write_stream(stream_after_tools)
    
    # Update the assistant message that initiated the tool calls with the final content,
    # or add a new one. Adding a new one is simpler.
    st.session_state.chat_history.append({"role": "assistant", "content": final_response_content})
    
    # Clean up for the next round of tool interactions
    st.session_state.tool_responses = [] 
    st.session_state.dialog_outcomes = {} 
    # tool_call_queue and current_tool_for_confirmation should be empty/None already
    st.rerun() # Rerun to reflect the final assistant message and clear state.
    
if show_history:
    st.write(st.session_state.chat_history)
