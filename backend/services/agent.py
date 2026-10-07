import json
from typing import Any
from backend.config import get_settings
from backend.services.browser import BrowserService
from backend.services.ollama import chat
from backend.utils.audit import record
from backend.utils.safety import evaluate_action

SYSTEM = """You are a browser workflow planner. Return ONLY a JSON object:
{"steps":[{"action":"open|click|fill|snapshot","value":"...","text":"..."}]}
Rules: open uses value=url; click uses value=CSS selector; fill uses value=CSS selector and text=field value; snapshot uses no value. Never plan payment, order submission, money transfer, credential theft, CAPTCHA bypass, or security bypass. Maximum 8 steps."""

async def plan_and_execute(goal: str, browser: BrowserService) -> dict[str, Any]:
    raw = await chat(f"{SYSTEM}\nGoal: {goal}")
    try:
        plan = json.loads(raw)
        steps = plan.get("steps")
        if not isinstance(steps, list) or len(steps) > get_settings().max_actions_per_request:
            raise ValueError("Invalid or oversized plan")
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        return {"status": "plan_rejected", "reason": str(exc), "model_output": raw[:4000]}

    results = []
    for step in steps:
        if not isinstance(step, dict):
            return {"status": "plan_rejected", "reason": "Each step must be an object", "results": results}
        action = str(step.get("action", "")).lower()
        value = str(step.get("value", ""))
        text = str(step.get("text", ""))
        decision = evaluate_action(f"{action} {value} {text}")
        if not decision.allowed:
            record("agent_blocked", {"action": action})
            return {"status": "blocked", "reason": decision.reason, "results": results}
        try:
            if action == "open":
                result = await browser.open(value)
            elif action == "click":
                result = await browser.click(value)
            elif action == "fill":
                result = await browser.fill(value, text)
            elif action == "snapshot":
                result = await browser.snapshot()
            else:
                return {"status": "plan_rejected", "reason": f"Unsupported action: {action}", "results": results}
            results.append({"action": action, "result": result})
        except Exception as exc:
            return {"status": "execution_error", "reason": str(exc), "results": results}
    record("agent_completed", {"goal_length": len(goal), "steps": len(results)})
    return {"status": "completed", "steps": results}
