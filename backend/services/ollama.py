import httpx
from typing import Any

from backend.config import get_settings


async def chat(
    prompt: str,
    images: list[str] | None = None,
    model: str | None = None,
) -> str:
    """Call the local Ollama chat API. Returns a graceful message if Ollama is down."""
    settings = get_settings()
    payload: dict[str, Any] = {
        "model": model or settings.ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if images:
        # Ollama expects raw base64 strings (no data: URI prefix).
        payload["messages"][0]["images"] = [img for img in images if img]

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return str(data.get("message", {}).get("content", "")).strip()
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        return (
            f"Ollama unavailable: {exc.__class__.__name__}. "
            "Deterministic browser tools remain available."
        )


async def vision_chat(prompt: str, image_base64: str) -> str:
    return await chat(prompt, images=[image_base64], model=get_settings().vision_model)
