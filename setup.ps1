# AI Consumer Behavior Assistant - Environment Setup (PowerShell)
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "AI Consumer Behavior Assistant - Environment Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create virtual environment
Write-Host "[1/4] Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv env
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "Virtual environment created successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Activate virtual environment
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\env\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Step 3: Upgrade pip
Write-Host "[3/4] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "Pip upgraded!" -ForegroundColor Green
Write-Host ""

# Step 4: Install requirements
Write-Host "[4/4] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install Ollama from https://ollama.ai" -ForegroundColor White
Write-Host "2. Pull Llama 3.2: ollama pull llama3.2" -ForegroundColor White
Write-Host "3. Start Ollama: ollama serve" -ForegroundColor White
Write-Host "4. In another terminal, activate venv and run:" -ForegroundColor White
Write-Host "   uvicorn main:app --reload" -ForegroundColor White
Write-Host "5. Open http://127.0.0.1:8000 in your browser" -ForegroundColor White
