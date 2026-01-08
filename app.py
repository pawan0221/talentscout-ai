import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

# --- SIDEBAR & SETUP ---
with st.sidebar:
    st.header("Configuration")
    
    # 1. API Key Setup
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Key loaded from secrets! ✅")
    else:
        api_key = st.text_input("Enter Google Gemini API Key", type="password")

    # 2. MODEL DEBUGGER & SELECTOR
    # This block fixes the 404 Error by finding what ACTUALLY exists
    selected_model_name = "gemini-pro" # default fallback
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Fetch all models that support content generation
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            st.markdown("---")
            st.write("🔹 **Available Models Detected:**")
            # Let user choose from the valid list
            selected_model_name = st.selectbox("Select Model", models, index=0 if models else 0)
        except Exception as e:
            st.error(f"Could not list models: {e}")

    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- PROMPT LOGIC ---
SYSTEM_INSTRUCTION = """
You are "TalentScout", a hiring assistant.
1. Ask for: Name, Email, Phone, Experience, Position, Location, Tech Stack (one by one).
2. AFTER Tech Stack is confirmed, generate 3-5 technical questions based specifically on that stack.
3. If user says 'exit', say goodbye.
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to TalentScout. What is your full name?"}
    ]

# --- HELPER FUNCTION ---
def get_gemini_response(user_input, history, model_name, api_key):
    if not api_key:
        return "⚠️ Please enter an API Key in the sidebar to continue."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name) # Use the specific name found in sidebar
        
        # Gemini history format
        chat = model.start_chat(history=history)
        response = chat.send_message(SYSTEM_INSTRUCTION + "\nUser: " + user_input)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN CHAT UI ---
st.title("TalentScout Hiring Assistant 🤖")

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Input
if prompt := st.chat_input("Type your response..."):
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare Gemini History
    gemini_history = []
    for msg in st.session_state.messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    import time

def get_gemini_response(user_input, history, model_name, api_key):
    if not api_key:
        return "⚠️ Please enter an API Key."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=history)
        
        # Try to send message
        response = chat.send_message(SYSTEM_INSTRUCTION + "\nUser: " + user_input)
        return response.text

    except Exception as e:
        error_msg = str(e)
        # Check for Quota Error (429)
        if "429" in error_msg:
            return "⚠️ **Quota Exceeded.** Please wait 1 minute or switch to a different model in the sidebar."
        return f"Error: {error_msg}"
