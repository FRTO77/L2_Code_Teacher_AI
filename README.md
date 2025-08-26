# Code_Teacher — AI Programming Mentor

Code_Teacher is a web app that teaches programming with interactive tasks, a code editor, automated tests, and AI hints.

## Stack
- **Python**
- **Streamlit** (web UI)
- **Monaco Editor** (via community components)
- **LangChain** (LLM hints/explanations)
- **Local Code Runner** (isolated subprocess)

## Features
- Task list with descriptions and starter code
- Monaco code editor with Python highlighting
- One-click Run Tests with detailed feedback
- AI hints and code explanations (OpenAI or Ollama)
- Session save/load and simple progress analytics

## Quick Start
1) Create and activate a virtual environment.
2) Install dependencies:
```bash
pip install -r requirements.txt
```
3) Create a `.env` from `.env.example` and set keys if using OpenAI (optional).
4) Run the app:
```bash
streamlit run app.py
```

## Configuration
- LLM provider and model can be set in the UI.
- Sessions are stored in `sessions/` as JSON.

## Safety Note
User code runs in a separate Python process with a short timeout and no external packages by default. This is a best-effort sandbox and not a security boundary. Avoid running untrusted code from others.

## License
MIT
