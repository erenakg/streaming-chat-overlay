@echo off
echo Starting Chat Overlay...
echo.
echo Controls:
echo - Ctrl+T: Toggle click-through mode
echo - Ctrl+Q or Escape: Close overlay
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import win32gui, webview" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the overlay
python main.py %*

pause
