# 📊 Chartbot: AI Consumer Behavior RAG Assistant

An efficient, fully local **Retrieval-Augmented Generation (RAG)** chatbot designed to analyze consumer behavior and documents. Powered by **FastAPI**, **Ollama + Llama 3.2**, and **Sentence Transformers**, Chartbot runs entirely on your local machine—keeping your data private and secure.

---

## 🛠️ System Architecture

Chartbot leverages a modern RAG pipeline to ingest data, generate embeddings, perform semantic search, and prompt a local Large Language Model (LLM) using retrieved context. 

### Architecture Diagram

The flow of data through the ingestion and inference pipelines is shown below:

```mermaid
graph TD
    subgraph Frontend [User Interface - SPA]
        UI[HTML5 / CSS / Vanilla JS Chat Interface]
    end

    subgraph Backend [FastAPI Backend]
        API[FastAPI Endpoints - main.py]
        RAG[RAGEngine Component]
        Cache[(Embeddings Cache - embeddings_cache.pkl)]
    end

    subgraph AI_Services [Local AI Engines]
        EmbedModel[sentence-transformers / all-MiniLM-L6-v2]
        Ollama[Ollama Server]
        Llama[Llama 3.2 3B Model]
    end

    subgraph Knowledge_Base [Knowledge Base - documents/]
        CSV[CSV Files, e.g., Customer Behavior.csv]
        TXT[TXT / MD Files]
    end

    %% Ingestion Pipeline
    CSV -->|Parse rows into sentences| RAG
    TXT -->|Read & chunk text| RAG
    RAG -->|Generate vector representations| EmbedModel
    EmbedModel -->|Return 384d embeddings| RAG
    RAG -->|Save/Load signature & vectors| Cache

    %% Inference / Chat Pipeline
    UI -->|1. POST /api/chat {message}| API
    API -->|2. Query| RAG
    RAG -->|3. Query Vector| EmbedModel
    EmbedModel -->|4. Query Embedding| RAG
    RAG -->|5. Cosine Similarity Match| Cache
    RAG -->|6. Retrieve top-k context| API
    API -->|7. Grounded Prompt + Context| Ollama
    Ollama -->|8. Local Inference| Llama
    Llama -->|9. Generated Response| Ollama
    Ollama -->|10. Answer Text| API
    API -->|11. JSON Response {answer, sources}| UI
```

---

## 🧩 Architectural Components

### 1. Document Ingestion & Parsing
* **Formats Supported**: Text (`.txt`), Markdown (`.md`), and CSV (`.csv`) files placed in the `documents/` directory.
* **Structured Data Handling**: For CSV files, rather than treating them as raw text, the `RAGEngine` reads rows using a `DictReader` and converts each record into a rich, natural-language sentence (e.g., `Record 1 — Age: 34; Gender: Female; Purchase_Category: Electronics.`) for semantic embedding.

### 2. Text Chunking & Token Optimization
* **Sliding Window Chunking**: Text documents are split into words and chunked using a configurable `CHUNK_SIZE` (default: 220 words) and `CHUNK_OVERLAP` (default: 40 words) to prevent information loss at chunk boundaries.

### 3. Local Embeddings Generation
* **Embedding Model**: Uses Hugging Face's `all-MiniLM-L6-v2` via `sentence-transformers`. This generates dense **384-dimensional vector representations** of document chunks.
* **Fully Offline**: Embeddings are computed locally on your CPU or GPU without making calls to third-party web services.

### 4. Smart Embeddings Cache System (`embeddings_cache.pkl`)
* **Signature-Based Invalidation**: On startup, Chartbot computes a fingerprint of all files (names, sizes, hashes) in the `documents/` directory.
* **Fast Startup**: If the fingerprint matches the cached signature, the pre-computed embeddings are loaded directly from disk in milliseconds, skipping the model-encoding phase entirely. If changes are detected, it re-indexes automatically.

### 5. Semantic Retrieval
* **Vector Similarity Search**: Incoming user questions are embedded using the same model. The engine computes the **Cosine Similarity** between the query vector and all chunk embeddings via a fast matrix multiplication (`numpy` matrix operations).
* **Top-K Selection**: Returns the top $k$ (default: 4) chunks with the highest scores, including their text, source filenames, and confidence scores.

### 6. Local LLM Grounding & Inference (Ollama)
* **API Integration**: Integrates with Ollama running locally at `http://localhost:11434`.
* **System Prompt Grounding**: Formulates a rigid system instruction forcing the Llama 3.2 model to answer *only* using the provided context and cite specific source numbers, mitigating model hallucinations.

---

## 💻 Tech Stack

* **Backend**: FastAPI (Python web framework), Pydantic (data validation), Uvicorn (ASGI server).
* **Machine Learning**: Sentence-Transformers (vector embeddings), NumPy (matrix operations, cosine similarity).
* **LLM Engine**: Ollama running Llama 3.2 (3B parameter model).
* **Frontend**: Vanilla HTML5, modern CSS3 (with CSS variables, flexbox, glassmorphism shadows), and Vanilla Javascript (asynchronous API calls, reactive status pooling).

---

## ⚡ API Endpoints

The backend exposes a clean HTTP interface:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the web-based Single Page Application (SPA). |
| `/api/chat` | `POST` | Accepts a user prompt and retrieves relevant document context to generate grounded responses. |
| `/api/reindex` | `POST` | Clears cache, re-reads documents, and regenerates embeddings. |
| `/health` | `GET` | Returns status checks, including chunk count and Ollama connectivity status. |

---

## 🚀 Quick Start

For detailed setup instructions, troubleshooting, and dependencies, see **[SETUP.md](file:///c:/Users/skmaz/Downloads/chartbot-main%20%281%29/chartbot-main/SETUP.md)**.

### 1. Ingest Documents
Place your `.txt`, `.md`, or `.csv` files into the `documents/` directory.

### 2. Set Up Environment
```bash
# Windows (Automatic)
setup.bat

# Manual
python -m venv env
source env/bin/activate  # env\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Run Ollama & Pull Llama 3.2
Make sure Ollama is installed and running, then pull the model:
```bash
ollama pull llama3.2
```

### 4. Launch Chartbot
```bash
# Windows (Automatic)
run.bat

# Manual
uvicorn main:app --reload
```
Open **`http://127.0.0.1:8000`** in your browser.