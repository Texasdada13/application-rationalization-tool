# Application Rationalization Tool - Auto-start Dashboard
# This script activates the virtual environment, starts the Flask server, and opens the browser

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Application Rationalization Tool - Starting Dashboard" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory (use current directory if running from VS Code)
if ($MyInvocation.MyCommand.Path) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $ScriptDir = Get-Location
}

Write-Host "Working directory: $ScriptDir" -ForegroundColor Gray
Write-Host ""

# Check if virtual environment exists
$VenvPath = Join-Path $ScriptDir "venv\Scripts\Activate.ps1"
if (-Not (Test-Path $VenvPath)) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Expected location: $VenvPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create a virtual environment by running:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    pause
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    . $VenvPath
    Write-Host "Virtual environment activated!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    pause
    exit 1
}

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
