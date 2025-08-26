import os
import json
from typing import Dict, Any
from pathlib import Path

import streamlit as st

from config import get_default_config, Config
from tasks import get_tasks, Task
from evaluator import evaluate_solution
from storage import save_session, list_sessions, load_session
from utils import truncate_text
from llm import ask_llm_for_text, build_hint_prompt, build_explain_prompt

# Try to import Monaco Editor variants, fallback to ACE or textarea
EditorKind = "textarea"

def _init_editor():
    global EditorKind
    try:
        from streamlit_monaco_editor import st_monaco_editor  # type: ignore
        EditorKind = "monaco_editor"
        return st_monaco_editor
    except Exception:
        pass
    try:
        from streamlit_monaco import st_monaco  # type: ignore
        EditorKind = "monaco"
        return st_monaco
    except Exception:
        pass
    try:
        import streamlit_ace as st_ace  # type: ignore
        EditorKind = "ace"
        return st_ace.st_ace
    except Exception:
        pass
    EditorKind = "textarea"
    return None

render_editor_component = _init_editor()

ASSETS_CSS = Path(__file__).resolve().parent / "assets" / "styles.css"
if ASSETS_CSS.exists():
    st.markdown(f"<style>{ASSETS_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="Code_Teacher", page_icon="👩‍🏫", layout="wide")

if "config" not in st.session_state:
    st.session_state.config = get_default_config()
if "code" not in st.session_state:
    st.session_state.code = {}
if "results" not in st.session_state:
    st.session_state.results = {}


def render_header():
    st.markdown("<div class='main-header'><h2>👩‍🏫 Code_Teacher — AI Programming Mentor</h2></div>", unsafe_allow_html=True)


def render_settings(cfg: Config) -> Config:
    with st.sidebar:
        st.subheader("Settings")
        provider = st.selectbox("LLM Provider", ["OpenAI", "Ollama", "None"], index=["OpenAI", "Ollama", "None"].index(cfg.llm_provider))
        if provider == "OpenAI":
            model = st.text_input("OpenAI Model", value=cfg.openai_model)
        elif provider == "Ollama":
            model = st.text_input("Ollama Model", value=cfg.ollama_model)
        else:
            model = ""
        temp = st.slider("AI Temperature", 0.0, 1.0, float(cfg.ai_temperature), 0.1)
        timeout = st.number_input("Execution Timeout (s)", min_value=1, max_value=20, value=int(cfg.execution_timeout_seconds))
        code_runner = st.selectbox("Code Runner", ["local", "interpreter_api"], index=["local", "interpreter_api"].index(cfg.code_runner))
        new_cfg = Config(
            llm_provider=provider,
            openai_model=model if provider == "OpenAI" else cfg.openai_model,
            ollama_model=model if provider == "Ollama" else cfg.ollama_model,
            ai_temperature=temp,
            execution_timeout_seconds=int(timeout),
            code_runner=code_runner,
        )
        return new_cfg


def render_task_selector(tasks):
    task_titles = [t.title for t in tasks]
    idx = st.sidebar.selectbox("Choose task", list(range(len(tasks))), format_func=lambda i: task_titles[i])
    return tasks[idx]


def render_editor(task: Task, cfg: Config) -> str:
    st.markdown(f"### 🧩 Task: {task.title}")
    with st.expander("Task Description", expanded=True):
        st.write(task.description)
    st.markdown("### ✍️ Your Solution")

    current_code = st.session_state.code.get(task.id, task.starter_code)

    if EditorKind == "monaco_editor" and render_editor_component:
        code = render_editor_component(value=current_code, language="python", height="420px", theme="vs-dark", key=f"editor_{task.id}")
    elif EditorKind == "monaco" and render_editor_component:
        code = render_editor_component(value=current_code, language="python", height="420px", theme="vs-dark", key=f"editor_{task.id}")
    elif EditorKind == "ace" and render_editor_component:
        code = render_editor_component(value=current_code, language="python", theme="monokai", key=f"editor_{task.id}", height=420)
    else:
        code = st.text_area("Code", current_code, height=420, key=f"editor_{task.id}")

    st.session_state.code[task.id] = code or ""
    return st.session_state.code[task.id]


def render_actions(task: Task, cfg: Config, user_code: str):
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        run = st.button("▶️ Run Tests", type="primary")
    with c2:
        hint = st.button("💡 Get Hint")
    with c3:
        explain = st.button("🧠 Explain Code")

    if run:
        res = evaluate_solution(user_code, task, timeout_seconds=int(cfg.execution_timeout_seconds))
        st.session_state.results[task.id] = res

    if hint:
        res = st.session_state.results.get(task.id)
        failing = []
        if res and res.get("details"):
            for d in res["details"]:
                if not d.get("ok"):
                    failing.append(f"- {d.get('description')}: expected={d.get('expected')} got={d.get('output')} error={d.get('error')}")
        details = "\n".join(failing) if failing else "No previous runs or all tests passed. Suggest potential edge cases."
        prompt = build_hint_prompt(task.title, task.description, details, user_code)
        text = ask_llm_for_text(cfg.llm_provider, cfg.openai_model if cfg.llm_provider=="OpenAI" else cfg.ollama_model, cfg.ai_temperature, prompt)
        if text:
            st.info(text)
        else:
            st.info("LLM not configured. Set provider and API key in .env if needed.")

    if explain:
        prompt = build_explain_prompt(task.title, task.description, user_code)
        text = ask_llm_for_text(cfg.llm_provider, cfg.openai_model if cfg.llm_provider=="OpenAI" else cfg.ollama_model, cfg.ai_temperature, prompt)
        if text:
            st.info(text)
        else:
            st.info("LLM not configured.")


def render_results(task: Task):
    res = st.session_state.results.get(task.id)
    st.markdown("### ✅ Results")
    if not res:
        st.write("Run tests to see results.")
        return
    if not res.get("success"):
        st.error(res.get("error") or "Execution failed")
        raw = res.get("raw")
        if raw:
            st.code(raw)
        return
    passed = res.get("pass_count", 0)
    total = res.get("total", 0)
    st.metric("Passed", f"{passed}/{total}")
    for d in res.get("details", []):
        cls = "result-pass" if d.get("ok") else "result-fail"
        st.markdown(f"<div class='{cls}'><b>{d.get('description')}</b><br/>expected={d.get('expected')} | output={d.get('output')} | error={d.get('error')}</div>", unsafe_allow_html=True)


def render_sessions_ui():
    with st.sidebar.expander("Sessions", expanded=False):
        name = st.text_input("Session name", value="")
        if st.button("💾 Save Session"):
            session = {
                "name": name or None,
                "code": st.session_state.code,
                "results": st.session_state.results,
            }
            p = save_session(session)
            st.success(f"Saved: {p.name}")
        st.write("Available:")
        files = list_sessions()
        if files:
            choice = st.selectbox("Load", [None] + files)
            if choice and st.button("📂 Load Selected"):
                data = load_session(choice)
                st.session_state.code = data.get("code", {})
                st.session_state.results = data.get("results", {})
                st.success("Session loaded")
        else:
            st.caption("No sessions yet")


def main():
    cfg = render_settings(st.session_state.config)
    st.session_state.config = cfg

    render_header()
    tasks = get_tasks()
    task = render_task_selector(tasks)

    user_code = render_editor(task, cfg)
    render_actions(task, cfg, user_code)
    render_results(task)
    render_sessions_ui()


if __name__ == "__main__":
    main()
