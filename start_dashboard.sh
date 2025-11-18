#!/bin/bash
# Application Rationalization Tool - Auto-start Dashboard
# This script activates the virtual environment, starts the Flask server, and opens the browser

echo "============================================================"
echo "Application Rationalization Tool - Starting Dashboard"
echo "============================================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
echo "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    echo "Please ensure the virtual environment exists at: $SCRIPT_DIR/venv"
    exit 1
fi

echo "Virtual environment activated!"
echo ""

# Wait 3 seconds then open browser in background
(sleep 3 && xdg-open "http://localhost:5000/dashboard" 2>/dev/null || open "http://localhost:5000/dashboard" 2>/dev/null) &

echo "Browser will open in 3 seconds..."
echo ""

# Change to web directory and start Flask
cd "$SCRIPT_DIR/web"

echo "Starting Flask server..."
echo "Dashboard URL: http://localhost:5000/dashboard"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the Flask app
python app.py
