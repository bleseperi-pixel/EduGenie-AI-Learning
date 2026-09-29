@echo off
cd /d "%~dp0"
if not exist .venv (echo Run setup.bat first. & pause & exit /b 1)
call .venv\Scripts\activate.bat
start "" http://127.0.0.1:8000
uvicorn main:app --reload
pause
