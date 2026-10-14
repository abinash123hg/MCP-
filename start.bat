@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title MCP WebPilot - Starting...
color 0A

echo ============================================
echo   MCP WebPilot - One-click start
echo ============================================
echo.

:: --- Ollama (optional; agent works better if running) ---
where ollama >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [1/4] Starting Ollama if not already running...
    start "Ollama" /MIN cmd /c "ollama serve"
    timeout /t 2 /nobreak >nul
) else (
    echo [1/4] Ollama not found in PATH - skipping.
    echo       Install from https://ollama.com if you need the AI agent.
)

:: --- Python check ---
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Install Python 3.12+ and tick "Add to PATH".
    pause
    exit /b 1
)

:: --- Virtual environment ---
echo [2/4] Checking virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo       Creating .venv ...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

:: --- Dependencies (fast if already installed) ---
echo [3/4] Ensuring dependencies...
pip install -r requirements.txt -q
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

:: Playwright browser (quiet; skips if present)
python -m playwright install chromium >nul 2>&1

:: --- Free / note port 8000 ---
echo [4/4] Starting server on http://localhost:8000 ...
echo.
echo   UI:     http://localhost:8000
echo   Health: http://localhost:8000/api/health
echo   MCP:    http://localhost:8000/mcp
echo.
echo   Close this window or press Ctrl+C to stop the server.
echo ============================================
echo.

:: Open Edge after a short delay (server boot) in a separate process
start "MCP-WebPilot-Edge" /MIN cmd /c "timeout /t 3 /nobreak >nul && start msedge http://localhost:8000"

:: Run API + static frontend together (same process)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

echo.
echo Server stopped.
pause
endlocal
