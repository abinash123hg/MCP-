@echo off
setlocal EnableExtensions
title MCP WebPilot - Stop

echo Stopping process on port 8000 (MCP WebPilot)...

for /f "tokens=5" %%P in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing PID %%P
    taskkill /PID %%P /F >nul 2>&1
)

echo Done. You can close this window.
timeout /t 2 >nul
endlocal
