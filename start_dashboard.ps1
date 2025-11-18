# Application Rationalization Tool - Auto-start Dashboard
# This script activates the virtual environment, starts the Flask server, and opens the browser

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Application Rationalization Tool - Starting Dashboard" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$ScriptDir\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Please ensure the virtual environment exists at: $ScriptDir\venv" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Wait 2 seconds then open browser in background
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:5000/dashboard"
} | Out-Null

Write-Host "Browser will open in 3 seconds..." -ForegroundColor Yellow
Write-Host ""

# Change to web directory and start Flask
Set-Location "$ScriptDir\web"

Write-Host "Starting Flask server..." -ForegroundColor Yellow
Write-Host "Dashboard URL: http://localhost:5000/dashboard" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start the Flask app
python app.py
