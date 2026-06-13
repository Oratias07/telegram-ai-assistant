# Install Telegram AI Bot as a Windows service using NSSM
# Run as Administrator

param(
    [string]$ServiceName = "telegram-ai-assistant",
    [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
)

$ErrorActionPreference = "Stop"

Write-Host "Installing $ServiceName as Windows service..."
Write-Host "Repo root: $RepoRoot"

# Check if NSSM is available
$NssmPath = (Get-Command nssm -ErrorAction SilentlyContinue).Source
if (-not $NssmPath) {
    Write-Host "ERROR: NSSM not found. Install NSSM from https://nssm.cc/download" -ForegroundColor Red
    Write-Host "Steps:" -ForegroundColor Yellow
    Write-Host "  1. Download NSSM from https://nssm.cc/download"
    Write-Host "  2. Extract it"
    Write-Host "  3. Add the nssm.exe folder to PATH, or place nssm.exe in a PATH directory"
    Write-Host "  4. Run this script again"
    exit 1
}

Write-Host "✓ NSSM found at: $NssmPath" -ForegroundColor Green

# Check if service already exists
$ServiceExists = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($ServiceExists) {
    Write-Host "WARNING: Service $ServiceName already exists. Removing old service first..." -ForegroundColor Yellow
    & nssm stop $ServiceName -ErrorAction SilentlyContinue
    & nssm remove $ServiceName confirm
}

# Create logs directory
$LogsDir = Join-Path $RepoRoot "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

Write-Host "✓ Logs directory: $LogsDir" -ForegroundColor Green

# Python executable
$PythonExe = Join-Path $RepoRoot "venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "ERROR: Python executable not found at $PythonExe" -ForegroundColor Red
    Write-Host "Make sure you have activated the venv or it exists." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Python: $PythonExe" -ForegroundColor Green

# Install service
Write-Host "Installing service..." -ForegroundColor Cyan
& nssm install $ServiceName "$PythonExe" "-m app.main"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install service" -ForegroundColor Red
    exit 1
}

# Configure service
Write-Host "Configuring service..." -ForegroundColor Cyan
& nssm set $ServiceName AppDirectory "$RepoRoot"
& nssm set $ServiceName AppStdoutCreationDisposition 4
& nssm set $ServiceName AppStdout "$LogsDir\service.out.log"
& nssm set $ServiceName AppStderrCreationDisposition 4
& nssm set $ServiceName AppStderr "$LogsDir\service.err.log"
& nssm set $ServiceName RestartDelay 5000
& nssm set $ServiceName Start SERVICE_AUTO_START

Write-Host "✓ Service configured" -ForegroundColor Green

# Start service
Write-Host "Starting service..." -ForegroundColor Cyan
& nssm start $ServiceName
Start-Sleep -Seconds 2

# Verify service is running
$Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($Service -and $Service.Status -eq "Running") {
    Write-Host "✓ Service installed and running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service info:" -ForegroundColor Yellow
    Write-Host "  Name: $ServiceName"
    Write-Host "  Status: Running"
    Write-Host "  Logs: $LogsDir\service.out.log and service.err.log"
    Write-Host ""
    Write-Host "To check status:" -ForegroundColor Yellow
    Write-Host "  Get-Service $ServiceName"
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "  Get-Content $LogsDir\service.out.log -Tail 20 -Wait"
} else {
    Write-Host "ERROR: Service failed to start. Check logs in $LogsDir" -ForegroundColor Red
    exit 1
}
