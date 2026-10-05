@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Please run:
    echo   python -m venv .venv
    echo   .\.venv\Scripts\Activate.ps1
    echo   python -m pip install -e ".[dev]"
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m uvicorn apps.mission_runner.web_app:app --host 127.0.0.1 --port 8000
