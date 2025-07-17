@echo off
echo Starting Stock Trading Agent...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check if model file exists
if not exist "model.pkl" (
    echo WARNING: model.pkl not found. You may need to train the model first.
    echo Check the realtime-evolution-strategy.ipynb notebook to train the model.
    pause
)

REM Check if data file exists
if not exist "TWTR.csv" (
    echo WARNING: TWTR.csv not found. The application may not work correctly.
    pause
)

REM Start the Flask application
echo Starting Flask application...
echo The application will be available at http://localhost:8005
echo Press Ctrl+C to stop the server
echo.
python app.py
