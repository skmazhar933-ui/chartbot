@echo off
echo Starting AI Consumer Behavior Assistant...
echo.

REM Activate virtual environment
call env\Scripts\activate.bat

REM Check if embeddings cache exists
if not exist "embeddings_cache.pkl" (
    echo First run detected - embeddings will be generated on first query
)

echo.
echo ================================================
echo FastAPI Server Starting
echo ================================================
echo Open your browser at: http://127.0.0.1:8000
echo API Docs at: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

REM Start the FastAPI application
uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
