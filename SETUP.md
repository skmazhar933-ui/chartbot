# Environment Setup Guide

This project is an AI RAG (Retrieval-Augmented Generation) Chatbot powered by FastAPI, Ollama, and Llama 3.2.

## Prerequisites

1. **Python 3.10+** - Download from [python.org](https://www.python.org/)
2. **Ollama** - Download from [ollama.ai](https://ollama.ai)

## Quick Setup

### Option 1: Using Batch Script (Easiest for Windows)

```bash
setup.bat
```

This script will:
- Create a Python virtual environment
- Activate it
- Upgrade pip
- Install all dependencies from `requirements.txt`

### Option 2: Using PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

### Option 3: Manual Setup

```bash
# Create virtual environment
python -m venv env

# Activate it
env\Scripts\activate.bat   # for Command Prompt
# OR
.\env\Scripts\Activate.ps1 # for PowerShell

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Install Ollama & Llama 3.2

```bash
# Download and install Ollama from https://ollama.ai

# Open a terminal and pull Llama 3.2
ollama pull llama3.2

# Keep Ollama running in the background
ollama serve
```

## Run the Application

### Option 1: Using Run Script
```bash
run.bat
```

### Option 2: Manual Start
```bash
# Activate virtual environment
env\Scripts\activate.bat

# Start the FastAPI server
uvicorn main:app --reload
```

## Access the Application

- **Frontend**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Swagger UI**: http://127.0.0.1:8000/swagger-ui

## Project Structure

```
chatbot/
├── main.py                    # FastAPI backend
├── index.html                 # Frontend UI
├── documents/                 # Your knowledge base files
│   └── Customer Behavior.csv
├── requirements.txt           # Python dependencies
├── setup.bat                  # Windows setup script
├── setup.ps1                  # PowerShell setup script
├── run.bat                    # Application run script
└── embeddings_cache.pkl       # Generated embeddings cache
```

## Environment Variables (Optional)

Create a `.env` file if you need custom settings:

```
OLLAMA_URL=http://localhost:11434/api/generate
MODEL_NAME=llama3.2
EMBED_MODEL_NAME=all-MiniLM-L6-v2
CHUNK_SIZE=220
CHUNK_OVERLAP=40
```

## Troubleshooting

### Issue: "python command not found"
- Make sure Python is installed and added to PATH
- Restart your terminal after installing Python

### Issue: Virtual environment activation fails
- Try using Command Prompt instead of PowerShell
- Or allow PowerShell script execution: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Issue: "ModuleNotFoundError"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Issue: "Connection refused" (Ollama)
- Make sure Ollama is running: `ollama serve`
- Check if it's on the correct URL: `http://localhost:11434`

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sentence-transformers** - Embedding model
- **requests** - HTTP client
- **numpy** - Numerical computing
- **pydantic** - Data validation

## First Run

The first time you ask a question:
1. The system will load the embedding model
2. Process documents in the `documents/` folder
3. Cache embeddings to `embeddings_cache.pkl`
4. Retrieve relevant chunks and query Llama 3.2
5. Return the answer with source citations

Subsequent queries will be faster as embeddings are cached.

## Need Help?

- Check the FastAPI docs: http://127.0.0.1:8000/docs
- Review `main.py` for available endpoints
- Check console output for errors
