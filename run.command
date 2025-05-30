#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if not already installed
if [ ! -f "requirements_installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    touch requirements_installed
fi

# Run the Flask application in background
echo "Starting Logo Cluster App..."
python app.py &
FLASK_PID=$!

# Wait a few seconds for Flask to start
echo "Waiting for server to start..."
sleep 1

# Open browser
echo "Opening browser..."
open http://127.0.0.1:5001

# Keep the terminal window open and handle cleanup
wait $FLASK_PID

# Keep the terminal window open
read -p "Press Enter to close..." 