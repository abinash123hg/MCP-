# MCP WebPilot

**B.Tech Final-Year Project — Local Multimodal MCP Browser Agent**

MCP WebPilot connects a local multimodal Ollama model to browser automation through the Model Context Protocol (MCP). The agent observes the current webpage using both structured DOM information and a browser screenshot, chooses one safe action, executes it through Playwright, and repeats until the task is complete or a safety boundary is reached.

## Architecture

```
User
 │
 ▼
Frontend
 │
 ▼
FastAPI Agent Loop
 │
 ├── Ollama (Gemma 3 4B)
 │      ├── text reasoning
 │      └── image understanding
 │
 ├── Safety / Audit
 │
 ▼
MCP Server
 │
 ▼
Playwright
 │
 ▼
Chromium
 ├── DOM/accessibility state
 └── screenshot
       │
       └──────► next agent decision
```

## Features

- MCP Streamable HTTP server
- FastAPI REST API
- Playwright Chromium automation
- Local Ollama multimodal model
- Iterative observe → decide → act → observe loop
- Screenshot-aware agent decisions
- DOM element inventory and robust locator fallbacks
- Persistent browser profile
- Safety gate and audit log
- Human-controlled boundary for irreversible workflows
- Live browser screenshot in the UI
- Docker + Compose
- Lightweight vanilla frontend
- Pytest + GitHub Actions

## Ollama model

The default model is **`gemma3:4b`** for both text and image input. Using one multimodal model avoids downloading a separate vision model.

```bash
ollama pull gemma3:4b
ollama run gemma3:4b
```

The model remains outside the Git repository.

## Run locally

```bash
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium
uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000`.

## Docker

```bash
docker compose up --build
```

Open `http://localhost:8000`.

For Docker, Ollama normally runs on the host and is reached through `host.docker.internal`.

## Agent workflow

Example:

```
User goal
   ↓
Observe DOM + screenshot
   ↓
Ollama chooses one action
   ↓
Backend validates action
   ↓
Playwright executes it
   ↓
Observe new state
   ↓
Repeat
```

The model is an untrusted planner. The backend is always the execution authority.

## Safety

The agent can navigate, inspect pages, click controls, and fill ordinary fields. Sensitive irreversible actions are stopped at the safety boundary and require explicit human handling.

The system does not provide unrestricted automation for transactions, security bypasses, credential theft, or verification challenges.

## Storage target

The repository does not contain models, browser binaries, virtual environments, datasets, or caches. The selected Ollama model is about 3.3 GB according to the current Ollama model listing, while project/runtime dependencies are kept lightweight. Exact total disk usage depends on the operating system, Python environment, browser cache, and Ollama storage.

## Project structure

```
frontend/                 Static UI
backend/main.py           FastAPI application
backend/mcp_server.py     MCP tool server
backend/services/         Browser + Ollama + agent
backend/utils/            Safety + audit
tests/                    Automated tests
docs/                     Architecture and safety
Dockerfile                Container image
compose.yaml              Docker Compose
requirements.txt          Python dependencies
```

## Academic scope

This project demonstrates MCP protocol integration, multimodal local-LLM reasoning, browser automation, agent loops, API design, safety engineering, containerization, testing, and auditability for a B.Tech final-year project.
