# MCP WebPilot

**B.Tech Final-Year Project — MCP-powered Safe Browser Automation Agent**

MCP WebPilot connects a local AI agent to browser automation through the Model Context Protocol (MCP). It can open websites, inspect pages, click, fill forms, and prepare checkout workflows while keeping irreversible actions behind an explicit human approval boundary.

## Architecture

```
Browser UI
   │ REST API
   ▼
FastAPI Backend ───── Ollama (optional local LLM)
   │
   ├── MCPServer
   │       │
   │       ▼
   │   BrowserService
   │       │
   │       ▼
   │    Playwright → Chromium
   │
   └── Safety / audit log
```

## Features

- MCP server with browser tools
- Playwright Chromium automation
- FastAPI REST API
- Optional Ollama local-model integration
- Persistent browser profile
- Safety gate for checkout/order/payment actions
- Current-page snapshot
- Audit logging
- Docker + Compose
- Lightweight vanilla frontend
- Pytest tests and GitHub Actions CI

## Storage target

The repository contains no browser binary, model, dataset, virtual environment, or `node_modules`. Docker downloads Chromium during image build. Ollama models remain outside the repository.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
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

## Optional Ollama

Set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` in `.env`. Browser tools remain usable when Ollama is unavailable.

## MCP endpoint

The MCP server is exposed at `/mcp` using Streamable HTTP.

## Safety model

Navigation and inspection can execute directly. Final order placement or payment submission is intentionally not exposed as an unrestricted MCP tool. The system can prepare a checkout workflow for human review.

## Project structure

```text
frontend/                 Static UI
backend/main.py           FastAPI application
backend/mcp_server.py     MCP tool server
backend/services/         Browser + Ollama + agent services
backend/utils/            Safety + audit utilities
tests/                    Automated tests
docs/                     Architecture and safety notes
Dockerfile                Container image
compose.yaml              Docker Compose
requirements.txt          Python dependencies
```

## Academic scope

This project demonstrates MCP protocol integration, tool calling, browser automation, local LLM integration, API design, containerization, safety engineering, testing, and auditability for a B.Tech final-year project.

## Agent workflow

Ollama proposes a strict JSON plan. The backend validates the plan against an allowlisted action set before executing it. The LLM is therefore treated as an untrusted planner; the backend remains the execution authority.
