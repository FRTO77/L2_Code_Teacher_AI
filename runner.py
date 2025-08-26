import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple


def run_python_in_subprocess(harness_code: str, timeout_seconds: int = 3) -> Tuple[int, str, str]:
    """Run given Python code in a separate process and return (returncode, stdout, stderr)."""
    with tempfile.TemporaryDirectory(prefix="ct_runner_") as tmpdir:
        tmp_path = Path(tmpdir)
        harness_path = tmp_path / "harness.py"
        harness_path.write_text(harness_code, encoding="utf-8")

        completed = subprocess.run(
            [sys.executable, "-u", str(harness_path)],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        return completed.returncode, completed.stdout, completed.stderr


def run_harness(harness_code: str, timeout_seconds: int = 3) -> Tuple[bool, str, str]:
    try:
        rc, out, err = run_python_in_subprocess(harness_code, timeout_seconds)
        return rc == 0, out, err
    except subprocess.TimeoutExpired as e:
        return False, "", f"Timeout after {timeout_seconds}s"
    except Exception as e:
        return False, "", f"Runner error: {str(e)}"
