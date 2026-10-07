from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from backend.mcp_server import browser, mcp, shutdown_browser
from backend.services.ollama import chat as ollama_chat
from backend.services.agent import plan_and_execute
from backend.utils.audit import record

mcp_app = mcp.streamable_http_app(streamable_http_path="/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("data").mkdir(exist_ok=True)
    async with mcp.session_manager.run():
        yield
    await shutdown_browser()

app = FastAPI(title="MCP WebPilot", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class OpenRequest(BaseModel):
    url: HttpUrl

class SelectorRequest(BaseModel):
    selector: str

class FillRequest(BaseModel):
    selector: str
    value: str

class ChatRequest(BaseModel):
    prompt: str

class AgentRequest(BaseModel):
    goal: str

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("frontend/index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "mcp-webpilot", "mcp_endpoint": "/mcp"}

@app.get("/api/status")
async def status():
    page = await browser.page()
    return {"url": page.url, "title": await page.title(), "mcp_endpoint": "/mcp"}

@app.post("/api/open")
async def open_page(request: OpenRequest):
    try:
        return await browser.open(str(request.url))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/api/snapshot")
async def snapshot():
    return await browser.snapshot()

@app.post("/api/click")
async def click(request: SelectorRequest):
    try:
        return await browser.click(request.selector)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/fill")
async def fill(request: FillRequest):
    try:
        return await browser.fill(request.selector, request.value)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/agent")
async def agent(request: AgentRequest):
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty")
    return await plan_and_execute(request.goal, browser)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    result = await ollama_chat(request.prompt)
    record("chat", {"prompt_length": len(request.prompt)})
    return {"response": result}

app.mount("/mcp", mcp_app)
