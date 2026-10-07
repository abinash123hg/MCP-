from datetime import datetime, timezone
from pathlib import Path
import json

LOG_PATH = Path("data/audit.log")

def record(event: str, payload: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    item = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "payload": payload}
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")
