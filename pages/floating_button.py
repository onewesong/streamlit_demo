import streamlit as st
from streamlit_extras.floating_button import floating_button

"""Example usage of the floating_button function."""
st.title("Floating action button demo")
st.write("See in the bottom right corner :wink:")

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]

# Chat dialog using decorator
@st.dialog("Chat Support", width="large")
def chat_dialog():
    # Create a container for chat messages with fixed height
    messages_container = st.container(height=400, border=False)

    # Display messages in the container
    with messages_container:
        # Display all messages from session state
        for message in st.session_state.messages:
            st.chat_message(message["role"]).write(message["content"])

    # Chat input (placed below the messages container in the UI)
    user_input = st.chat_input("Type a message...")

    # Handle new user input
    if user_input:
        messages_container.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Add bot response to chat history
        messages_container.chat_message("assistant").write(
            "Thanks for your message! This is a demo response."
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Thanks for your message! This is a demo response.",
            }
        )

# Handle FAB button click to open the dialog
if floating_button(":material/chat: Chat"):
    chat_dialog()

