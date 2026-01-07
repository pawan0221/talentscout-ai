import streamlit as st
import google.generativeai as genai

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
        st.session_state.chat_history = []
        st.rerun()

# --- PROMPT ENGINEERING ---
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
        if "python" in user_input.lower():
            return "Since you mentioned Python, here are 3 questions: 1. What are Python decorators? 2. Explain list comprehensions. 3. Difference between .py and .pyc files?"
        return "I am in DEMO mode. Please provide a Google API Key. (Simulated: Please tell me your email address?)"

    try:
        # 1. Configure the API
        genai.configure(api_key=api_key)
        
        # 2. Define the Model
        # CHANGED: Switched to 'gemini-pro' to fix 404 error
        model = genai.GenerativeModel("gemini-pro")

        # 3. Start Chat with History
        # Note: gemini-pro handles system instructions differently, so we inject it into the first prompt context if needed,
        # or rely on the chat history context we build below.
        chat = model.start_chat(history=history)
        
        # 4. Send Message (Prepending system instruction hidden in context if new chat)
        # For simplicity in this fix, we send the user input directly. 
        # The prompt engineering in the history usually guides the model sufficiently.
        response = chat.send_message(SYSTEM_INSTRUCTION + "\n\nUser Input: " + user_input if not history else user_input)
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
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Check for Exit Keywords
    if prompt.lower() in ["exit", "quit", "stop", "bye"]:
        goodbye_msg = "Thank you! Your details have been recorded. A recruiter will be in touch. Goodbye!"
        with st.chat_message("assistant"):
            st.markdown(goodbye_msg)
        st.session_state.messages.append({"role": "assistant", "content": goodbye_msg})
        st.stop()

    # 3. Prepare History for Gemini
    gemini_history = []
    for msg in st.session_state.messages[:-1]: 
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # 4. Fetch Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = get_gemini_response(prompt, gemini_history, api_key)
            st.markdown(response_text)

    # 5. Update UI History
    st.session_state.messages.append({"role": "assistant", "content": response_text})
