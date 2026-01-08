import streamlit as st
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="⚡")

# --- SIDEBAR & SETUP ---
with st.sidebar:
    st.header("Configuration")
    st.write("Powered by **Groq**")
    
    # 1. API Key Setup
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("Key loaded from secrets! ✅")
    else:
        api_key = st.text_input("Enter Groq API Key (gsk_...)", type="password")

    # 2. Model Selector
    # UPDATED: Using currently active Groq models
    model_options = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    selected_model = st.selectbox("Select Model", model_options, index=0)

    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- PROMPT LOGIC ---
SYSTEM_PROMPT = """
You are "TalentScout", a professional hiring assistant for a tech recruitment agency.

1. **Phase 1: Screening.** Collect these details one by one (do not ask all at once):
   - Full Name
   - Email
   - Phone
   - Years of Experience
   - Desired Position
   - Location
   - Tech Stack

2. **Phase 2: Technical Check.** - ONCE the user confirms their Tech Stack, generate 3-5 challenging technical questions specific to those tools.
   - Ask the user to answer them.

3. **Rules:**
   - Keep responses concise.
   - If the user says "exit" or "quit", conclude the interview professionally.
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello! Welcome to TalentScout. I'm here to assist with your initial screening. To get started, could you please tell me your full name?"}
    ]

# --- HELPER FUNCTION ---
def get_groq_response(messages, model_name, api_key):
    if not api_key:
        return "⚠️ Please enter your Groq API Key in the sidebar."

    try:
        client = Groq(api_key=api_key)
        
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN CHAT UI ---
st.title("TalentScout Hiring Assistant ⚡")

# Display History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle Input
if prompt := st.chat_input("Type your response..."):
    # 1. Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Check Exit
    if prompt.lower() in ["exit", "quit", "bye"]:
        goodbye_msg = "Thank you for your time. Your application has been recorded. Goodbye!"
        with st.chat_message("assistant"):
            st.markdown(goodbye_msg)
        st.session_state.messages.append({"role": "assistant", "content": goodbye_msg})
        st.stop()

    # 3. Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = get_groq_response(
                st.session_state.messages, 
                selected_model, 
                api_key
            )
            st.markdown(response_text)
    
    # 4. Save AI Response
    st.session_state.messages.append({"role": "assistant", "content": response_text})
