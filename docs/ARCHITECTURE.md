# Architecture

## Layers

1. **Frontend** — sends safe browser commands to the API and displays snapshots.
2. **FastAPI** — HTTP boundary, validation, lifecycle, and static UI serving.
3. **MCP server** — standardized tool interface for an MCP host/model.
4. **Browser service** — one persistent Playwright Chromium context.
5. **Safety layer** — blocks irreversible purchase/payment actions from unrestricted execution.
6. **Ollama service** — optional local reasoning/planning endpoint.
7. **Audit layer** — append-only JSON-lines activity log.

## Why MCP?

MCP standardizes how an AI host discovers and calls tools. The browser automation logic stays behind typed tool boundaries instead of being embedded into a model prompt.

## Resource constraints

No model weights, browser binaries, datasets, or Python environments are stored in Git. Docker builds the runtime and a named volume stores only the browser profile. Ollama remains an external local service.
