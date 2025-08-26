from dataclasses import dataclass, asdict
import os
from typing import Any, Dict


@dataclass
class Config:
    llm_provider: str = os.getenv("LLM_PROVIDER", "OpenAI")  # OpenAI | Ollama | None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3:8b-instruct")
    ai_temperature: float = float(os.getenv("AI_TEMPERATURE", "0.3"))

    execution_timeout_seconds: int = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "3"))
    max_output_chars: int = 8000

    code_runner: str = os.getenv("CODE_RUNNER", "local")  # local | interpreter_api

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)


def get_default_config() -> Config:
    return Config()
