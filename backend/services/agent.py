import json
from typing import Any
from backend.config import get_settings
from backend.services.browser import BrowserService
from backend.services.ollama import chat
from backend.utils.audit import record
from backend.utils.safety import evaluate_action

SYSTEM = """You are the controller of a safe browser agent.
Return ONLY valid JSON:
{"action":"open|click|fill|snapshot|done","value":"...","text":"...","reason":"..."}

Rules:
- open value is a URL.
- click value can be CSS, text=..., role=button|Name, placeholder=..., or label=...
- fill value identifies an input with CSS, placeholder=..., or label=...
- Use the supplied element list instead of inventing selectors.
- Use done when the goal is complete.
- If the requested workflow reaches an irreversible or sensitive final step, return done with reason "approval_required".
- Never bypass security controls or verification challenges.
"""

def _clean_json(raw: str) -> dict[str, Any] | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                return None
    return None

async def plan_and_execute(goal: str, browser: BrowserService) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    settings = get_settings()

    for step_number in range(1, settings.max_agent_steps + 1):
        state = await browser.snapshot(include_screenshot=True)
        image = state.pop("screenshot_base64")
        prompt = (
            f"{SYSTEM}\nGoal: {goal}\nStep: {step_number}/{settings.max_agent_steps}\n"
            f"Current webpage state:\n{json.dumps(state, ensure_ascii=False)[:18000]}"
        )
        raw = await chat(prompt, images=[image])
        decision = _clean_json(raw)

        if not decision:
            return {
                "status": "plan_rejected",
                "reason": "Model did not return valid JSON",
                "model_output": raw[:4000],
                "results": results,
            }

        action = str(decision.get("action", "")).lower()
        value = str(decision.get("value", ""))
        text = str(decision.get("text", ""))

        if action == "done":
            reason = str(decision.get("reason", "completed"))
            record("agent_stopped", {"reason": reason, "steps": len(results)})
            return {
                "status": "approval_required" if reason == "approval_required" else "completed",
                "reason": reason,
                "results": results,
            }

        if action not in {"open", "click", "fill", "snapshot"}:
            return {"status": "plan_rejected", "reason": f"Unsupported action: {action}", "results": results}

        safety = evaluate_action(f"{action} {value} {text}")
        if not safety.allowed:
            record("agent_blocked", {"action": action, "reason": safety.reason})
            return {"status": "blocked", "reason": safety.reason, "results": results}

        try:
            if action == "open":
                result = await browser.open(value)
            elif action == "click":
                result = await browser.click(value)
            elif action == "fill":
                result = await browser.fill(value, text)
            else:
                result = await browser.snapshot()
            results.append({"step": step_number, "action": action, "result": result})
        except Exception as exc:
            record("agent_error", {"step": step_number, "error": str(exc)[:500]})
            return {"status": "execution_error", "reason": str(exc), "results": results}

    return {
        "status": "max_steps_reached",
        "reason": "Agent step limit reached",
        "results": results,
    }
