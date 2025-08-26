from typing import Any, Dict, Optional
import os

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None  # type: ignore

try:
    from langchain_ollama import ChatOllama
except Exception:
    ChatOllama = None  # type: ignore


def make_llm(provider: str, model: str, temperature: float):
    if provider == "OpenAI" and ChatOpenAI is not None and os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model=model, temperature=temperature, api_key=os.getenv("OPENAI_API_KEY"))
    if provider == "Ollama" and ChatOllama is not None:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=temperature)
    return None


HINT_SYSTEM_PROMPT = (
    "You are a helpful programming mentor. Provide concise, step-by-step hints without revealing the full solution."
)


def build_hint_prompt(task_title: str, task_description: str, failing_details: str, user_code: str) -> str:
    return (
        f"Task: {task_title}\n"
        f"Description: {task_description}\n"
        f"Failing details: {failing_details}\n"
        f"User code:\n{user_code}\n\n"
        "Give 1-3 short hints (bullet list), focusing on the bug or missing cases."
    )


def build_explain_prompt(task_title: str, task_description: str, user_code: str) -> str:
    return (
        f"Task: {task_title}\n"
        f"Description: {task_description}\n"
        f"User code:\n{user_code}\n\n"
        "Explain what this code does and suggest one improvement."
    )


def ask_llm_for_text(provider: str, model: str, temperature: float, prompt: str) -> Optional[str]:
    llm = make_llm(provider, model, temperature)
    if llm is None:
        return None
    try:
        # Both ChatOpenAI and ChatOllama implement invoke for LCEL
        resp = llm.invoke(prompt)
        if hasattr(resp, "content"):
            return resp.content
        # fallback: str
        return str(resp)
    except Exception as e:
        return f"LLM error: {str(e)}"
