import streamlit as st
import os
from openai import OpenAI

# ================== OPENAI CLIENT ==================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================== STREAMLIT CONFIG ==================
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🤖",
    layout="centered"
)

# ================== SESSION STATE ==================
if "step" not in st.session_state:
    st.session_state.step = "name"

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []

if "tech_q_index" not in st.session_state:
    st.session_state.tech_q_index = 0

# ================== UI HEADER ==================
st.title("🤖 TalentScout AI")
st.caption("AI Hiring Assistant – Initial Screening")
st.markdown("🔒 *Session-only. No personal data is stored.*")
st.divider()

# ================== STEP QUESTIONS (DETERMINISTIC) ==================
STEP_QUESTIONS = {
    "name": "What is your **full name**?",
    "email": "What is your **email address**?",
    "phone": "What is your **phone number**?",
    "experience": "How many **years of experience** do you have?",
    "position": "Which **position** are you applying for?",
    "location": "What is your **current location**?",
    "tech_stack": "Please list your **tech stack** (languages, frameworks, tools)."
}

STEP_ORDER = [
    "name",
    "email",
    "phone",
    "experience",
    "position",
    "location",
    "tech_stack",
    "technical_questions",
    "end"
]

# ================== INITIAL BOT MESSAGE ==================
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hello! 👋 I’m **TalentScout**, your AI hiring assistant.\n\n"
            f"{STEP_QUESTIONS['name']}"
        )
    })

# ================== DISPLAY CHAT ==================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================== USER INPUT ==================
user_input = st.chat_input("Type your answer here (or 'exit' to quit)")

# ================== EXIT HANDLING ==================
if user_input and user_input.lower() in ["exit", "quit", "bye"]:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Thank you for your time! 🙌\n\n"
            "Our HR team will contact you within **48 hours**.\n\n"
            "Wishing you the best! 🚀"
        )
    })
    st.stop()

# ================== PROCESS INPUT ==================
if user_input:
    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    step = st.session_state.step

    # -------- DATA COLLECTION STEPS --------
    if step in STEP_QUESTIONS:
        st.session_state.candidate[step] = user_input

        next_step_index = STEP_ORDER.index(step) + 1
        st.session_state.step = STEP_ORDER[next_step_index]

        next_step = st.session_state.step

        if next_step in STEP_QUESTIONS:
            st.session_state.messages.append({
                "role": "assistant",
                "content": STEP_QUESTIONS[next_step]
            })

    # -------- TECHNICAL QUESTIONS (LLM) --------
    elif step == "technical_questions":

        # First time → generate questions
        if not st.session_state.tech_questions:
            with st.spinner("Generating technical questions…"):
                prompt = f"""
You are a technical interviewer.

Candidate tech stack:
{st.session_state.candidate.get("tech_stack")}

Generate exactly 3 technical interview questions.
Return them as a numbered list.
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": prompt}],
                    temperature=0.4
                )

                questions_text = response.choices[0].message.content
                st.session_state.tech_questions = [
                    q.strip("0123456789. ").strip()
                    for q in questions_text.split("\n")
                    if q.strip()
                ]

        # Ask next technical question
        idx = st.session_state.tech_q_index

        if idx < len(st.session_state.tech_questions):
            st.session_state.messages.append({
                "role": "assistant",
                "content": st.session_state.tech_questions[idx]
            })
            st.session_state.tech_q_index += 1
        else:
            st.session_state.step = "end"
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    f"Thank you, **{st.session_state.candidate.get('name')}**! 🙌\n\n"
                    "We’ve completed the initial screening.\n\n"
                    "📌 **Next Steps:**\n"
                    "• HR will review your responses\n"
                    "• You’ll hear back within **48 hours**\n\n"
                    "Best of luck! 🚀"
                )
            })

    # -------- MOVE TO TECH QUESTIONS --------
    if st.session_state.step == "technical_questions" and not st.session_state.tech_questions:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Great! Let’s move on to a few technical questions."
        })

