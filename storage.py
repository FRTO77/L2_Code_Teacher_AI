import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

SESSIONS_DIR = Path(__file__).resolve().parent / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def save_session(session: Dict[str, Any]) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = session.get("name") or f"session_{ts}"
    path = SESSIONS_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    return path


def list_sessions() -> List[str]:
    return sorted([p.name for p in SESSIONS_DIR.glob("*.json")])


def load_session(filename: str) -> Dict[str, Any]:
    path = SESSIONS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
