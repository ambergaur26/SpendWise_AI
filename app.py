import streamlit as st
import requests

st.title("💰 Expense Manager Bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
user_input = st.chat_input("Enter salary or expense...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json={"user_message": user_input}
    )

    # Debug safety
    if response.status_code != 200:
        st.error(f"Backend error: {response.status_code}")
        st.stop()

    bot_data = response.json()

    # Safe extraction
    reply = bot_data.get("reply", "⚠️ No reply from server.")
    remaining = bot_data.get("remaining", 0)
    warning = bot_data.get("warning")
    trajectory = bot_data.get("trajectory")

    final_message = reply
    final_message += f"\n\n💰 Remaining Balance: ₹{remaining}"

    if warning:
        final_message += f"\n\n{warning}"

    if trajectory:
        final_message += f"\n\n{trajectory}"

    st.session_state.messages.append(
        {"role": "assistant", "content": final_message}
    )

    st.rerun()
