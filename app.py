import streamlit as st
import os
import re
import google.generativeai as genai

# ================= GEMINI CONFIG =================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ================= STREAMLIT CONFIG =================
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🤖",
    layout="centered"
)

# ================= VALIDATION FUNCTIONS =================
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def is_valid_phone(phone):
    return re.match(r"^\+?\d{8,15}$", phone)

def is_valid_experience(exp):
    return exp.isdigit() and 0 <= int(exp) <= 50

# ================= SESSION STATE =================
if "step" not in st.session_state:
    st.session_state.step = "name"

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []

if "tech_index" not in st.session_state:
    st.session_state.tech_index = 0

if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False

# ================= UI HEADER =================
st.title("🤖 TalentScout AI")
st.caption("AI Hiring Assistant – Initial Screening")
st.markdown("🔒 *Session-only. No personal data is stored.*")
st.divider()

# ================= QUESTIONS =================
QUESTIONS = {
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
    "technical",
    "end"
]

# ================= INITIAL MESSAGE =================
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hello! 👋 I’m **TalentScout**, your AI hiring assistant.\n\n"
            f"{QUESTIONS['name']}"
        )
    })

# ================= DISPLAY CHAT =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================= USER INPUT =================
user_input = st.chat_input("Type your answer here (or 'exit' to quit)")

# ================= EXIT =================
if user_input and user_input.lower() in ["exit", "quit", "bye"]:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Thank you for your time! 🙌\n\n"
            "Our HR team will contact you within **48 hours**.\n\n"
            "Best of luck! 🚀"
        )
    })
    st.stop()

# ================= PROCESS INPUT =================
if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    step = st.session_state.step
    error = None

    # ---------- VALIDATION ----------
    if step == "email" and not is_valid_email(user_input):
        error = "❌ Please enter a valid email address (example: name@gmail.com)."

    elif step == "phone" and not is_valid_phone(user_input):
        error = "❌ Please enter a valid phone number (8–15 digits, numbers only)."

    elif step == "experience" and not is_valid_experience(user_input):
        error = "❌ Please enter experience as a number (e.g., 2, 5, 10)."

    # ---------- DATA COLLECTION ----------
    if step in QUESTIONS:
        if error:
            st.session_state.messages.append({
                "role": "assistant",
                "content": error + "\n\n" + QUESTIONS[step]
            })
        else:
            st.session_state.candidate[step] = user_input
            next_step = STEP_ORDER[STEP_ORDER.index(step) + 1]
            st.session_state.step = next_step

            if next_step in QUESTIONS:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": QUESTIONS[next_step]
                })

            if next_step == "technical":
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Great! Now let’s move on to a few technical questions."
                })
                st.session_state.awaiting_answer = False

    # ---------- TECHNICAL QUESTIONS (GEMINI) ----------
    elif step == "technical":

        if st.session_state.awaiting_answer:
            st.session_state.tech_index += 1
            st.session_state.awaiting_answer = False

        if not st.session_state.tech_questions:
            prompt = f"""
You are a technical interviewer.

Candidate tech stack:
{st.session_state.candidate.get("tech_stack")}

Generate exactly 3 technical interview questions.
Return one question per line only.
"""
            response = model.generate_content(prompt)
            st.session_state.tech_questions = [
                q.strip() for q in response.text.split("\n") if q.strip()
            ]

        if st.session_state.tech_index < len(st.session_state.tech_questions):
            st.session_state.messages.append({
                "role": "assistant",
                "content": st.session_state.tech_questions[st.session_state.tech_index]
            })
            st.session_state.awaiting_answer = True
        else:
            st.session_state.step = "end"
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    f"Thank you, **{st.session_state.candidate.get('name')}**! 🙌\n\n"
                    "We’ve completed the initial screening.\n\n"
                    "📌 **Next Steps:**\n"
                    "• HR will review your profile\n"
                    "• You’ll hear back within **48 hours**\n\n"
                    "Best of luck! 🚀"
                )
            })

