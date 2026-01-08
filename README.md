# TalentScout AI Hiring Assistant ⚡

**TalentScout** is an intelligent, AI-powered hiring assistant built with **Streamlit** and **Groq**. It is designed to streamline the recruitment process by performing initial candidate screenings, collecting essential details, and generating dynamic technical interview questions based on the candidate's specific tech stack.

## 🚀 Features

* **⚡ Ultra-Fast Responses:** Powered by Groq's LPU inference engine for near-instant conversational flow.
* **🤖 Conversational Interface:** Natural, context-aware interaction using Llama 3 or Mixtral models.
* **📝 Automated Screening:** Step-by-step collection of candidate details (Name, Experience, Position, etc.).
* **👨‍💻 Dynamic Tech Assessment:** Generates 3-5 challenging technical questions specific to the user's declared skills (e.g., Python, React, AWS).
* **🔒 Privacy-First:** No permanent database storage; data exists only during the active session.

## 🧠 Tech Stack

* **Frontend / UI:** [Streamlit](https://streamlit.io/)
* **LLM Inference:** [Groq API](https://groq.com/)
* **Models Supported:** Llama 3 (8b/70b), Mixtral 8x7b, Gemma 7b
* **Language:** Python 3.9+

## 🔐 Data Privacy & Security

* **Session-Based:** All candidate data is stored in volatile memory (`st.session_state`) and is cleared upon refresh or exit.
* **Secure Keys:** API keys are managed via Streamlit Secrets or secure UI input, never hardcoded.
* **GDPR Compliance:** Designed with data minimization principles; no PII is persisted after the chat ends.

## ▶️ Run Locally

### 1. Clone the Repository
```bash
git clone <your-repo-link>
cd talentscout-ai
