# DRISHTI backend launcher - activates the project's own venv automatically.
# Usage:  .\run.ps1          (from anywhere)
#         powershell -File .\run.ps1

$ErrorActionPreference = "Stop"

# Resolve repo layout regardless of where the script is invoked from
$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir    = Join-Path $BackendDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

# Create the venv if it doesn't exist yet
if (-not (Test-Path $VenvPython)) {
    Write-Host "[run.ps1] .venv not found - creating it..." -ForegroundColor Yellow
    python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment" }
}

# Activate the venv for this session
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) { & $ActivateScript }

# Install dependencies only when missing (first run)
$Check = & $VenvPython -c "import fastapi, uvicorn, sqlalchemy, jwt, sklearn, cv2, PIL, multipart" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[run.ps1] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt")
}

Write-Host "[run.ps1] Starting DRISHTI API on http://127.0.0.1:8000 (docs at /docs)" -ForegroundColor Green
Set-Location $BackendDir

# Use `python -m pip` / `python -m uvicorn` style invocation:
# immune to broken hardcoded launcher paths even if the venv moves later.
& $VenvPython -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
