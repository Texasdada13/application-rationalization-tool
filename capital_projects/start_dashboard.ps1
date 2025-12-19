# Capital Projects Lifecycle Planner - Startup Script
# Run this script to start the web dashboard

$ErrorActionPreference = "Stop"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Capital Projects Lifecycle Planner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

# Check for virtual environment
$venvPath = Join-Path $rootDir "venv"
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvActivate
} else {
    Write-Host "No virtual environment found, using system Python" -ForegroundColor Yellow
}

# Set PYTHONPATH
$env:PYTHONPATH = $scriptDir

# Change to web directory
$webDir = Join-Path $scriptDir "web"
Set-Location $webDir

Write-Host ""
Write-Host "Starting Capital Projects Dashboard..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://localhost:5001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the Flask app
python app.py
