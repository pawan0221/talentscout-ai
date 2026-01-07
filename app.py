import streamlit as st
import openai
from datetime import datetime

# --- CONFIGURATION & SETUP ---
# [cite: 17, 18, 53] Setting up Streamlit Page Configuration
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

# --- SIDEBAR & API SETUP ---
with st.sidebar:
    st.header("Configuration")
    st.write("This bot uses OpenAI's GPT models.")
    # In a real production environment, use st.secrets or environment variables
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    
    st.info(
        "**Note:** To run this locally, you need an OpenAI API Key. "
        "If you don't have one, the bot will use a simulated mode for UI demonstration."
    )
    
    # [cite: 21] Exit button to clear session
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.candidate_info = {}
        st.rerun()

# --- PROMPT ENGINEERING [cite: 10, 57] ---
# This system prompt defines the persona, goals, and logic for the LLM.
# It covers Information Gathering [cite: 22], Tech Stack declaration[cite: 32],
# and Question Generation[cite: 34].

SYSTEM_PROMPT = """
You are the intelligent Hiring Assistant for "TalentScout", a recruitment agency. 
Your goal is to screen candidates by gathering information and asking technical questions.

### PHASE 1: INFORMATION GATHERING
You must collect the following details. Be conversational, do not ask for everything in one massive list. Ask for 1-2 items at a time to maintain a natural flow.
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

### RULES & BEHAVIOR
- **Context Awareness:** Remember previous answers.
- **Fallback:** If the user asks about the weather or general topics, politely steer them back to the hiring process.
- **Exit:** If the user says "exit", "quit", or "bye", thank them and end the conversation[cite: 45].
- **Tone:** Professional, encouraging, and efficient.
"""

# --- SESSION STATE INITIALIZATION ---
#  Maintaining context of the conversation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello! Welcome to TalentScout. I'm here to assist with your initial screening. To get started, could you please tell me your full name?"} # [cite: 20] Greeting
    ]

# --- HELPER FUNCTIONS ---

def get_llm_response(messages, api_key):
    """
    Fetches response from OpenAI GPT. 
    [cite: 54] Utilizing pre-trained models.
    """
    if not api_key:
        # SIMULATED RESPONSE for demo purposes if no key is provided [cite: 67]
        last_user_msg = messages[-1]["content"].lower()
        if "python" in last_user_msg:
            return "Great. Since you mentioned Python, here are 3 technical questions:\n1. Explain list comprehensions.\n2. What is the GIL?\n3. Difference between list and tuple."
        return "I am in DEMO mode. Please provide an API key to have a real conversation. (Simulated: Please tell me your email address?)"

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or gpt-4
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN UI LAYOUT ---
# [cite: 17] Clean and intuitive UI

st.title("TalentScout Hiring Assistant 🤖")
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    # Hide system prompt from UI
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input Handling
if prompt := st.chat_input("Type your response here..."):
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Append to history 
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Check for Exit Keywords 
    if prompt.lower() in ["exit", "quit", "stop", "bye"]:
        goodbye_msg = "Thank you for your time. Your details have been recorded. A recruiter will be in touch soon. Goodbye!"
        with st.chat_message("assistant"):
            st.markdown(goodbye_msg)
        st.session_state.messages.append({"role": "assistant", "content": goodbye_msg})
        st.stop()

    # 4. Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = get_llm_response(st.session_state.messages, api_key)
            st.markdown(response_text)
            
    # 5. Append Assistant Response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- DOCUMENTATION / README SECTION (In-App) ---
# [cite: 72] README Requirements embedded for clarity
with st.expander("📝 Project Documentation & Logic"):
    st.markdown("""
    ### Project Overview
    This chatbot serves as a screen for **TalentScout**, automating the collection of candidate data and testing technical proficiency.
    
    ### Functionality
    * **Greeting:** Auto-initializes context[cite: 20].
    * **Data Collection:** Prompts for Name, Email, Phone, Experience, Position, Location, and Tech Stack .
    * **Technical Questions:** Uses LLM logic to detect "Tech Stack" inputs and dynamically generates 3-5 relevant questions[cite: 34].
    * **Privacy:** No data is stored permanently; `session_state` is volatile (clears on refresh)[cite: 66].
    
    ### Tech Stack
    * **Frontend:** Streamlit 
    * **Logic:** Python 3.9+ [cite: 49]
    * **AI:** OpenAI GPT-3.5/4 (via API) [cite: 54]
    """)
