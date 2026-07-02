@echo off
echo ================================================
echo AI Consumer Behavior Assistant - Environment Setup
echo ================================================
echo.

REM Create virtual environment
echo [1/4] Creating Python virtual environment...
python -m venv env
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Upgrade pip
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip
echo Pip upgraded!
echo.

REM Install requirements
echo [4/4] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Install Ollama from https://ollama.ai
echo 2. Pull Llama 3.2: ollama pull llama3.2
echo 3. Start Ollama: ollama serve
echo 4. In another terminal, activate venv and run:
echo    uvicorn main:app --reload
echo 5. Open http://127.0.0.1:8000 in your browser
echo.
pause
