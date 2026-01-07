import streamlit as st
import os
from openai import OpenAI

# ================== CONFIG ==================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🤖",
    layout="centered"
)

# ================== SYSTEM PROMPT ==================
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are TalentScout, a professional AI hiring assistant.

Rules:
- Ask ONE question at a time
- Be friendly, concise, and professional
- Collect candidate details step-by-step:
  Full Name, Email, Phone Number, Experience,
  Desired Position, Location, Tech Stack
- Generate 3–5 technical questions based on the tech stack
- Maintain conversation context
- Do NOT store personal data (GDPR compliant)
- End politely and mention HR will contact within 48 hours
"""
}

# ================== SESSION STATE ==================
if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_PROMPT]

if "started" not in st.session_state:
    st.session_state.started = False

# ================== UI ==================
st.title("🤖 TalentScout AI")
st.caption("AI Hiring Assistant – Initial Candidate Screening")
st.markdown("🔒 *Session-only. No data is stored.*")
st.divider()

# ================== GREETING ==================
if not st.session_state.started:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hello! 👋 I’m **TalentScout**, your AI hiring assistant.\n\n"
            "Let’s get started — what’s your **full name**?"
        )
    })
    st.session_state.started = True

# ================== DISPLAY CHAT ==================
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================== USER INPUT ==================
user_input = st.chat_input("Type your answer here (or 'exit' to quit)")

if user_input:
    # Exit keywords
    if user_input.lower() in ["exit", "quit", "bye"]:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "Thank you for your time! 🙌\n\n"
                "Our HR team will contact you within **48 hours**.\n\n"
                "Wishing you the best! 🚀"
            )
        })
        st.stop()

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Call OpenAI (NEW API)
    with st.spinner("TalentScout is typing…"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                temperature=0.4
            )

            reply = response.choices[0].message.content

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })

        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ Sorry, something went wrong. Please try again."
            })

