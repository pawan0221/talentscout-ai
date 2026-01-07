import streamlit as st
import openai
import os

# Read OpenAI key from Streamlit Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🤖",
    layout="centered"
)

# SYSTEM PROMPT
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are TalentScout, a professional AI hiring assistant.

Rules:
- Ask ONE question at a time
- Collect: Name, Email, Phone, Experience, Position, Location, Tech Stack
- Generate 3–5 technical questions based on the candidate's tech stack
- Maintain context
- Be polite and professional
- End by informing HR will contact within 48 hours
- Do not store personal data (GDPR compliant)
"""
}

# Initialize chat memory
if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_PROMPT]

if "started" not in st.session_state:
    st.session_state.started = False

# UI Header
st.title("🤖 TalentScout AI")
st.caption("AI Hiring Assistant – Initial Screening")
st.markdown("🔒 Session-only. No data is stored.")
st.divider()

# First message
if not st.session_state.started:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! 👋 I’m **TalentScout**, your AI hiring assistant.\n\nWhat’s your **full name**?"
    })
    st.session_state.started = True

# Display chat messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
user_input = st.chat_input("Type your answer here (or 'exit' to quit)")

if user_input:
    # Exit keywords
    if user_input.lower() in ["exit", "quit", "bye"]:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Thank you for your time! 🙌\n\nOur HR team will contact you within **48 hours**."
        })
        st.stop()

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Call OpenAI
    with st.spinner("TalentScout is typing…"):
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            temperature=0.4
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })
