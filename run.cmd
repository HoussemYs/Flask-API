@echo off

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Set environment variables
set PYTHONDONTWRITEBYTECODE=1
set FLASK_DEBUG=1
set FLASK_ENV=development
set FLASK_APP=src\app.py

REM Start the Flask server
flask run --host=0.0.0.0 --port=5000
