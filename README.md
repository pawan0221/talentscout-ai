# TalentScout AI Hiring Assistant

TalentScout is an AI-powered hiring assistant built with **Streamlit** and **Google Gemini**.
It helps recruiters perform initial candidate screening by collecting candidate details
and asking technical questions based on the candidate’s declared tech stack.

---

## 🚀 Features

- Conversational chatbot interface
- Step-by-step candidate information collection
- Input validation (email, phone, experience)
- Tech stack–based technical interview questions
- Context-aware interaction
- GDPR-compliant (session-only data, no storage)

---

## 🧠 Tech Stack

- **Frontend / UI:** Streamlit
- **LLM:** Google Gemini (gemini-1.5-flash)
- **Language:** Python
- **Deployment:** Streamlit Community Cloud

---

## 🔐 Data Privacy

- No personal data is stored
- All information exists only during the active session
- API keys are managed securely using Streamlit Secrets
- GDPR-safe by design

---

## ▶️ Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
