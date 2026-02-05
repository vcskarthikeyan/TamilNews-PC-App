@echo off
REM =====================================================
REM Tamil News Dashboard - Windows Setup & Launch
REM =====================================================

title Tamil News Dashboard - Setup

echo.
echo ================================================
echo   TAMIL NEWS DASHBOARD - SETUP
echo ================================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python is not installed!
    echo.
    echo Please install Python 3.7 or higher:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python found
echo.

REM Check pip
echo [2/4] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found, installing...
    python -m ensurepip --default-pip
)
echo ✅ pip ready
echo.

REM Install dependencies
echo [3/4] Installing dependencies...
echo This may take a minute...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to install dependencies
    echo.
    echo Try running manually:
    echo pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo ✅ All dependencies installed
echo.

REM Start server
echo [4/4] Starting server...
echo.
echo ================================================
echo   SERVER STARTING
echo ================================================
echo.
echo   URL: http://localhost:5000
echo   Port: 5000
echo.
echo   Keep this window open while using the dashboard
echo   Press Ctrl+C to stop the server
echo.
echo ================================================
echo.

python tamil_news_server_final.py

REM If server stops
echo.
echo.
echo ================================================
echo   SERVER STOPPED
echo ================================================
echo.
pause
