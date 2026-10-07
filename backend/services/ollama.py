import httpx
from backend.config import get_settings

async def chat(prompt: str) -> str:
    settings = get_settings()
    payload = {"model": settings.ollama_model, "prompt": prompt, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{settings.ollama_base_url.rstrip('/')}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", "")).strip()
    except (httpx.HTTPError, ValueError) as exc:
        return f"Ollama unavailable: {exc.__class__.__name__}. Deterministic tools remain available."
