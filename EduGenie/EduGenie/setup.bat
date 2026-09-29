@echo off
cd /d "%~dp0"
echo === EduGenie setup ===
python --version >nul 2>&1 || (echo Python not found. Install Python 3.10+ and tick "Add Python to PATH". & pause & exit /b 1)
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-lite.txt
if not exist .env (
  copy .env.example .env >nul
  powershell -Command "(Get-Content .env) -replace EXPLAIN_BACKEND=local,EXPLAIN_BACKEND=gemini | Set-Content .env"
)
echo.
echo Setup done. Now open .env and paste your GEMINI_API_KEY, then run run.bat
notepad .env
pause
