import json
from typing import Any, Dict
from textwrap import dedent
from tasks import Task
from runner import run_harness


def _build_harness(user_code: str, task: Task) -> str:
    tests_json = json.dumps([
        {
            "description": tc.description,
            "args": tc.input_args,
            "kwargs": tc.input_kwargs,
            "expected": tc.expected_output,
        }
        for tc in task.tests
    ], ensure_ascii=False)

    parts = []
    parts.append("# --- user solution ---\n")
    parts.append(user_code)
    parts.append("\n\n# --- test harness ---\n")
    parts.append("import json, time, traceback\n\n")
    parts.append("RESULT = {\"pass_count\": 0, \"total\": 0, \"details\": []}\n\n")
    parts.append("def _run_one(func, case):\n")
    parts.append("    try:\n")
    parts.append("        out = func(*case[\"args\"], **case[\"kwargs\"])\n")
    parts.append("        ok = out == case[\"expected\"]\n")
    parts.append("        return ok, None, out\n")
    parts.append("    except Exception as e:\n")
    parts.append("        err_msg = type(e).__name__ + ': ' + str(e)\n")
    parts.append("        return False, err_msg, None\n\n")
    parts.append("def main():\n")
    parts.append(f"    cases = json.loads(r'''{tests_json}''')\n")
    parts.append(f"    from __main__ import {task.function_name} as target\n")
    parts.append("    RESULT[\"total\"] = len(cases)\n")
    parts.append("    for case in cases:\n")
    parts.append("        ok, err, out = _run_one(target, case)\n")
    parts.append("        if ok:\n")
    parts.append("            RESULT[\"pass_count\"] += 1\n")
    parts.append("        RESULT[\"details\"].append({\n")
    parts.append("            \"description\": case[\"description\"],\n")
    parts.append("            \"ok\": ok,\n")
    parts.append("            \"expected\": case[\"expected\"],\n")
    parts.append("            \"output\": out,\n")
    parts.append("            \"error\": err,\n")
    parts.append("        })\n")
    parts.append("    print(json.dumps(RESULT, ensure_ascii=False))\n\n")
    parts.append("if __name__ == \"__main__\":\n")
    parts.append("    main()\n")

    return "".join(parts)


def evaluate_solution(user_code: str, task: Task, timeout_seconds: int = 3) -> Dict[str, Any]:
    harness = _build_harness(user_code, task)
    ok, out, err = run_harness(harness, timeout_seconds=timeout_seconds)
    if not ok:
        return {
            "success": False,
            "error": err or "Execution failed",
            "raw": out,
        }
    try:
        data = json.loads(out.strip())
        data["success"] = True
        return data
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Invalid harness output",
            "raw": out,
        }
