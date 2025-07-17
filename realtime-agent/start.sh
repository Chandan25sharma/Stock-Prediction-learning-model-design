#!/bin/bash

echo "Starting Stock Trading Agent..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if model file exists
if [ ! -f "model.pkl" ]; then
    echo "WARNING: model.pkl not found. You may need to train the model first."
    echo "Check the realtime-evolution-strategy.ipynb notebook to train the model."
    read -p "Press Enter to continue..."
fi

# Check if data file exists
if [ ! -f "TWTR.csv" ]; then
    echo "WARNING: TWTR.csv not found. The application may not work correctly."
    read -p "Press Enter to continue..."
fi

# Start the Flask application
echo "Starting Flask application..."
echo "The application will be available at http://localhost:8005"
echo "Press Ctrl+C to stop the server"
echo
python app.py
