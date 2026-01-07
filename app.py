import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION & SETUP ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

# --- SIDEBAR & API SETUP ---
with st.sidebar:
    st.header("Configuration")
    st.write("Powered by **Google Gemini Pro**")
    
    # Securely input API Key
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    
    st.info(
        "**Note:** You can get a free API key from Google AI Studio. "
        "The bot will use simulated responses if no key is provided."
    )
    
    # Button to reset the conversation
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.chat_history = []  # Specific history format for Gemini
        st.rerun()

# --- PROMPT ENGINEERING ---
# We pass this system instruction to the model configuration.
SYSTEM_INSTRUCTION = """
You are the intelligent Hiring Assistant for "TalentScout", a recruitment agency. 
Your goal is to screen candidates by gathering information and asking technical questions.

### PHASE 1: INFORMATION GATHERING
You must collect the following details. Be conversational; ask for 1-2 items at a time.
Required Information:
1. Full Name
2. Email Address
3. Phone Number
4. Years of Experience
5. Desired Position
6. Current Location
7. Tech Stack (Languages, Frameworks, Tools)

### PHASE 2: TECHNICAL SCREENING
Once (and only once) you have confirmed the candidate's **Tech Stack**, you must generate 3-5 technical interview questions tailored specifically to their stack. 
- Example: If they know Python and Django, ask about decorators or Django ORM.
- Present these questions to the candidate and ask them to answer briefly.

### RULES
- **Context Awareness:** Remember previous answers.
- **Fallback:** If the user deviates (e.g., asks about weather), politely steer them back.
- **Exit:** If the user says "exit", "quit", or "bye", thank them and end the conversation.
"""

# --- SESSION STATE INITIALIZATION ---
# We store messages for the UI and a separate history list for the Gemini API
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to TalentScout. I'm here to assist with your initial screening. To get started, could you please tell me your full name?"}
    ]

# --- HELPER FUNCTIONS ---

def get_gemini_response(user_input, history, api_key):
    """
    Interacts with the Google Gemini API.
    """
    if not api_key:
        # SIMULATED RESPONSE for testing without burning quota or if key is missing
        if "python" in user_input.lower():
            return "Since you mentioned Python, here are 3 questions: 1. What are Python decorators? 2. Explain list comprehensions. 3. Difference between .py and .pyc files?"
        return "I am in DEMO mode. Please provide a Google API Key. (Simulated: Please tell me your email address?)"

    try:
        # 1. Configure the API
        genai.configure(api_key=api_key)
        
        # 2. Define the Model
        # We use 'gemini-1.5-flash' for speed/cost or 'gemini-pro' for reasoning
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )

        # 3. Start Chat with History
        # Gemini expects history as a list of Content objects or dicts: 
        # [{'role': 'user', 'parts': ['...']}, {'role': 'model', 'parts': ['...']}]
        chat = model.start_chat(history=history)
        
        # 4. Send Message
        response = chat.send_message(user_input)
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN UI LAYOUT ---

st.title("TalentScout Hiring Assistant 🤖")
st.markdown("---")

# 1. Display Chat History (UI Only)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Handle User Input
if prompt := st.chat_input("Type your response here..."):
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to UI history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Check for Exit Keywords
    if prompt.lower() in ["exit", "quit", "stop", "bye"]:
        goodbye_msg = "Thank you! Your details have been recorded. A recruiter will be in touch. Goodbye!"
        with st.chat_message("assistant"):
            st.markdown(goodbye_msg)
        st.session_state.messages.append({"role": "assistant", "content": goodbye_msg})
        st.stop()

    # 3. Prepare History for Gemini
    # We must convert our UI history (Streamlit format) to Gemini format.
    # Streamlit uses "assistant", Gemini uses "model".
    gemini_history = []
    for msg in st.session_state.messages[:-1]: # Exclude the very last prompt we just added, as we send that separately
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # 4. Fetch Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = get_gemini_response(prompt, gemini_history, api_key)
            st.markdown(response_text)

    # 5. Update UI History
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- DOCUMENTATION ---
with st.expander("📝 Project Documentation"):
    st.markdown("""
    ### Project Overview
    This chatbot screens candidates for **TalentScout**. It uses Google's Gemini model to conduct a natural language interview.
    
    ### Functionality
    * **Information Gathering:** Collects Name, Email, Experience, etc. [cite: 24-31].
    * **Context Management:** Uses `model.start_chat(history=...)` to maintain conversation flow[cite: 40].
    * **Tech Questions:** Dynamically generates questions based on user-provided tech stack [cite: 34-37].
    
    ### Libraries Used
    * `streamlit`: User Interface.
    * `google-generativeai`: Interaction with Gemini LLM.
    """)
