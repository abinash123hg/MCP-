import httpx
from typing import Any
from backend.config import get_settings

async def chat(prompt: str, images: list[str] | None = None, model: str | None = None) -> str:
    settings = get_settings()
    payload: dict[str, Any] = {
        "model": model or settings.ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if images:
        payload["messages"][0]["images"] = images
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return str(data.get("message", {}).get("content", "")).strip()
    except (httpx.HTTPError, ValueError) as exc:
        return f"Ollama unavailable: {exc.__class__.__name__}. Deterministic tools remain available."

async def vision_chat(prompt: str, image_base64: str) -> str:
    return await chat(prompt, images=[image_base64], model=get_settings().vision_model)
