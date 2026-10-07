from mcp.server import MCPServer
from backend.config import get_settings
from backend.services.browser import BrowserService
from backend.services.ollama import chat as ollama_chat
from backend.utils.audit import record
from backend.utils.safety import evaluate_action

settings = get_settings()
browser = BrowserService(settings.headless, settings.browser_timeout_ms)
mcp = MCPServer(
    "MCP WebPilot",
    instructions="Safe browser automation server. Final irreversible purchase/payment actions require human approval and are never exposed as unrestricted tools."
)

@mcp.tool()
async def browser_open(url: str) -> dict:
    """Open a URL in the controlled Chromium session."""
    decision = evaluate_action(f"open {url}")
    if not decision.allowed:
        raise ValueError(decision.reason)
    result = await browser.open(url)
    record("browser_open", {"url": url})
    return result

@mcp.tool()
async def browser_snapshot() -> dict:
    """Return the current page URL, title, and visible text."""
    result = await browser.snapshot()
    record("browser_snapshot", {"url": result["url"]})
    return result

@mcp.tool()
async def browser_click(selector: str) -> dict:
    """Click the first element matching a CSS selector."""
    decision = evaluate_action(f"click {selector}")
    if not decision.allowed:
        raise ValueError(decision.reason)
    result = await browser.click(selector)
    record("browser_click", {"selector": selector})
    return result

@mcp.tool()
async def browser_fill(selector: str, value: str) -> dict:
    """Fill a form field using a CSS selector."""
    result = await browser.fill(selector, value)
    record("browser_fill", {"selector": selector})
    return result

@mcp.tool()
async def prepare_purchase(site_url: str, product_query: str) -> dict:
    """Navigate to a shopping site and prepare a human-reviewable purchase workflow. Never places the final order."""
    await browser.open(site_url)
    result = await browser.snapshot()
    record("prepare_purchase", {"site_url": site_url, "product_query": product_query})
    return {
        "status": "prepared_for_review",
        "product_query": product_query,
        "page": result,
        "next_step": "Use browser tools to inspect and select the product. Final payment/order submission is intentionally not an MCP tool."
    }

@mcp.tool()
async def ask_local_model(prompt: str) -> str:
    """Ask the configured local Ollama model for reasoning or planning assistance."""
    result = await ollama_chat(prompt)
    record("ask_local_model", {"prompt_length": len(prompt)})
    return result

async def shutdown_browser() -> None:
    await browser.close()
