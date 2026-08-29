@echo off
REM Simple one-shot vendoring: just runs the python script
cd /d "%~dp0"
backend\.venv\Scripts\python.exe fetch_swagger.py
exit /b %ERRORLEVEL%