@echo off
REM P.U.L.S.E Development Server Launcher
REM Starts both backend (FastAPI) and frontend (Next.js) servers

setlocal enabledelayedexpansion

echo 🚀 Starting P.U.L.S.E Development Environment...
echo ================================================================

REM Get the project root directory
set "PROJECT_ROOT=%~dp0"

REM Start Backend
echo 📚 Starting Backend (FastAPI)...
cd /d "%PROJECT_ROOT%backend"
start "P.U.L.S.E Backend" cmd /k "python main.py"

timeout /t 2 /nobreak

REM Start Frontend
echo 🎨 Starting Frontend (Next.js)...
cd /d "%PROJECT_ROOT%frontendV2"
start "P.U.L.S.E Frontend" cmd /k "npm run dev"

echo.
echo ================================================================
echo ✅ Both servers are starting in separate windows!
echo.
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:3000
echo.
echo    Close the terminal windows to stop the servers.
echo ================================================================

pause
