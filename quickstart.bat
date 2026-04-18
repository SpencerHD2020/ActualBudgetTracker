@echo off
setlocal enabledelayedexpansion
echo Budget Tracker - Quick Start
echo ============================
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install -r requirements.txt > nul 2>&1

echo Initializing database...
python -c "import database; database.init_database()"

echo.
echo Launching application...
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Application crashed with exit code !errorlevel!
    echo.
    echo Press any key to close this window...
    pause
    exit /b 1
)

echo.
echo Application closed normally.
pause
