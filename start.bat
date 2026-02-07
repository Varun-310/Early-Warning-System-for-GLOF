@echo off
title GLOF Monitoring System
color 0A

echo.
echo ══════════════════════════════════════════════════════════════
echo                    GLOF MONITORING SYSTEM                     
echo                       Starting All Services                    
echo ══════════════════════════════════════════════════════════════
echo.

REM Get the directory where this batch file is located
set "BASE_DIR=%~dp0"

echo [1/6] Starting API Gateway (Port 8000)...
start /B /MIN "" cmd /c "cd /d "%BASE_DIR%Backend\gateway" && py main.py > nul 2>&1"
timeout /t 2 /nobreak >nul

echo [2/6] Starting GLOF Service (Port 8001)...
start /B /MIN "" cmd /c "cd /d "%BASE_DIR%Backend\GLOF" && py main.py > nul 2>&1"
timeout /t 1 /nobreak >nul

echo [3/6] Starting SAR Service (Port 8002)...
start /B /MIN "" cmd /c "cd /d "%BASE_DIR%Backend\SAR" && py main.py > nul 2>&1"
timeout /t 1 /nobreak >nul

echo [4/6] Starting Lake Service (Port 8003)...
start /B /MIN "" cmd /c "cd /d "%BASE_DIR%Backend\lake_size" && py main.py > nul 2>&1"
timeout /t 1 /nobreak >nul

echo [5/6] Starting Terrain Service (Port 8004)...
start /B /MIN "" cmd /c "cd /d "%BASE_DIR%Backend\srtm & motionOfWaves" && py main.py > nul 2>&1"
timeout /t 1 /nobreak >nul

echo [6/6] Starting Frontend (Port 5173)...
start /B /MIN "" cmd /c "cd /d "%BASE_DIR%Frontend\glof-dashboard" && npm run dev > nul 2>&1"

echo.
echo ══════════════════════════════════════════════════════════════
echo                    ALL SERVICES STARTED!                       
echo ══════════════════════════════════════════════════════════════
echo.
echo   API Gateway:      http://localhost:8000
echo   GLOF Service:     http://localhost:8001
echo   SAR Service:      http://localhost:8002
echo   Lake Service:     http://localhost:8003
echo   Terrain Service:  http://localhost:8004
echo   Frontend:         http://localhost:5173
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo Opening dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo All services are running in the background.
echo To stop all services, run: taskkill /F /IM py.exe /T
echo.
pause
