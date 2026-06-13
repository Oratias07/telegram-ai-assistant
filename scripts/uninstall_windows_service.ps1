# Uninstall Telegram AI Bot Windows service
# Run as Administrator

param(
    [string]$ServiceName = "telegram-ai-assistant"
)

$ErrorActionPreference = "Stop"

Write-Host "Uninstalling $ServiceName service..." -ForegroundColor Cyan

# Check if NSSM is available
$NssmPath = (Get-Command nssm -ErrorAction SilentlyContinue).Source
if (-not $NssmPath) {
    Write-Host "ERROR: NSSM not found in PATH" -ForegroundColor Red
    exit 1
}

# Check if service exists
$ServiceExists = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $ServiceExists) {
    Write-Host "Service $ServiceName not found" -ForegroundColor Yellow
    exit 0
}

# Stop service
Write-Host "Stopping service..." -ForegroundColor Yellow
& nssm stop $ServiceName -ErrorAction SilentlyContinue

# Remove service
Write-Host "Removing service..." -ForegroundColor Yellow
& nssm remove $ServiceName confirm

Write-Host "✓ Service uninstalled" -ForegroundColor Green
