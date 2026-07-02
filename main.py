"""
app.py
------
A self-contained FastAPI RAG chatbot backend powered by Ollama + Llama 3.2.

- Loads .txt / .md files from ./documents
- Chunks + embeds them locally with sentence-transformers (cached to disk)
- Retrieves the top-k most relevant chunks for each question (cosine similarity)
- Sends the question + retrieved context to Llama 3.2 via Ollama
- Serves index.html (which contains all of the frontend HTML/CSS/JS)

Run:
    pip install -r requirements.txt
    ollama pull llama3.2
    ollama serve            # if not already running
    uvicorn app:app --reload

Then open http://127.0.0.1:8000
"""

import csv
import os
import pickle

import numpy as np
import requests
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DOCS_DIR = "documents"
CACHE_FILE = "embeddings_cache.pkl"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 220
CHUNK_OVERLAP = 40

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

SYSTEM_PROMPT = (
    "You are a precise research assistant. Answer the user's question using ONLY "
    "the information in the provided context. If the context does not contain the "
    "answer, say plainly that you don't have that information. Keep answers concise "
    "and cite which source number(s) you used, e.g. (Source 2)."
)


# ---------------------------------------------------------------------------
# RAG engine
# ---------------------------------------------------------------------------
class RAGEngine:
    def __init__(
        self,
        docs_dir: str = DOCS_DIR,
        cache_file: str = CACHE_FILE,
        model_name: str = EMBED_MODEL_NAME,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        self.docs_dir = docs_dir
        self.cache_file = cache_file
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.model = SentenceTransformer(model_name)
        self.chunks: list[dict] = []  # [{"text": ..., "source": ...}]
        self.embeddings: np.ndarray = np.zeros((0, self.model.get_sentence_embedding_dimension()))

        self._build_index()

    # -- indexing ----------------------------------------------------------
    def _load_documents(self) -> list[tuple[str, str]]:
        docs = []
        if not os.path.isdir(self.docs_dir):
            return docs
        for fname in sorted(os.listdir(self.docs_dir)):
            if fname.lower().endswith((".txt", ".md")):
                path = os.path.join(self.docs_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    docs.append((fname, f.read()))
        return docs

    def _row_to_sentence(self, row: dict, row_num: int) -> str:
        """Turn a CSV row dict into a natural-language sentence for embedding."""
        parts = [f"{key.strip()}: {str(value).strip()}" for key, value in row.items() if value not in (None, "")]
        return f"Record {row_num} \u2014 " + "; ".join(parts) + "."

    def _load_csv_rows(self) -> list[tuple[str, str]]:
        """Return [(sentence, source_filename), ...] for every row of every .csv file."""
        rows = []
        if not os.path.isdir(self.docs_dir):
            return rows
        for fname in sorted(os.listdir(self.docs_dir)):
            if fname.lower().endswith(".csv"):
                path = os.path.join(self.docs_dir, fname)
                with open(path, "r", encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader, start=1):
                        rows.append((self._row_to_sentence(row, i), fname))
        return rows

    def _chunk_text(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return []
        chunks = []
        step = max(self.chunk_size - self.chunk_overlap, 1)
        for i in range(0, len(words), step):
            piece = " ".join(words[i : i + self.chunk_size])
            if piece.strip():
                chunks.append(piece)
            if i + self.chunk_size >= len(words):
                break
        return chunks

    def _signature(self, docs: list[tuple[str, str]], csv_rows: list[tuple[str, str]]) -> tuple:
        """Cheap fingerprint of the document set, used to invalidate the cache."""
        doc_sig = tuple((name, len(text), hash(text)) for name, text in docs)
        csv_sig = tuple((src, hash(sentence)) for sentence, src in csv_rows)
        return (doc_sig, csv_sig)

    def _build_index(self) -> None:
        docs = self._load_documents()
        csv_rows = self._load_csv_rows()
        sig = self._signature(docs, csv_rows)

        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    cached = pickle.load(f)
                if cached.get("signature") == sig:
                    self.chunks = cached["chunks"]
                    self.embeddings = cached["embeddings"]
                    return
            except Exception:
                pass  # cache unreadable/corrupted -> rebuild

        self.chunks = []
        for fname, text in docs:
            for chunk in self._chunk_text(text):
                self.chunks.append({"text": chunk, "source": fname})
        for sentence, fname in csv_rows:
            self.chunks.append({"text": sentence, "source": fname})

        if self.chunks:
            texts = [c["text"] for c in self.chunks]
            self.embeddings = self.model.encode(
                texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
            )
        else:
            self.embeddings = np.zeros((0, self.model.get_sentence_embedding_dimension()))

        with open(self.cache_file, "wb") as f:
            pickle.dump(
                {"signature": sig, "chunks": self.chunks, "embeddings": self.embeddings}, f
            )

    def reindex(self) -> int:
        """Force a rebuild of the index (e.g. after adding new documents)."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self._build_index()
        return len(self.chunks)

    # -- retrieval -----------------------------------------------------------
    def retrieve(self, query: str, top_k: int = 4) -> list[dict]:
        if not self.chunks:
            return []
        q_emb = self.model.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
        )[0]
        scores = self.embeddings @ q_emb
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [
            {
                "text": self.chunks[i]["text"],
                "source": self.chunks[i]["source"],
                "score": float(scores[i]),
            }
            for i in top_idx
        ]


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="RAG Chatbot (Llama 3.2)")
rag = RAGEngine()


class ChatRequest(BaseModel):
    message: str
    top_k: int = 4


class SourceChunk(BaseModel):
    source: str
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


@app.get("/")
async def index():
    return FileResponse("index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    query = req.message.strip()
    if not query:
        return ChatResponse(answer="Please enter a question.", sources=[])

    top_k = max(1, min(req.top_k, 10))
    chunks = rag.retrieve(query, top_k=top_k)

    context = "\n\n".join(
        f"[Source {i + 1}: {c['source']}]\n{c['text']}" for i, c in enumerate(chunks)
    )

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context if context else '(no relevant documents found)'}\n\n"
        f"Question: {query}\n\n"
        f"Answer:"
    )

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        answer = resp.json().get("response", "").strip() or "(empty response from model)"
    except requests.exceptions.RequestException as e:
        answer = (
            "Could not reach Ollama. Make sure it's running and the model is pulled:\n"
            "  ollama pull llama3.2\n"
            "  ollama serve\n"
            f"Details: {e}"
        )

    sources = [
        SourceChunk(source=c["source"], text=c["text"], score=round(c["score"], 3))
        for c in chunks
    ]
    return ChatResponse(answer=answer, sources=sources)


@app.post("/api/reindex")
async def reindex():
    count = rag.reindex()
    return {"status": "ok", "chunks_indexed": count}


@app.get("/health")
async def health():
    ollama_ok = False
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        ollama_ok = r.ok
    except requests.exceptions.RequestException:
        ollama_ok = False

    return {
        "status": "ok",
        "model": MODEL_NAME,
        "chunks_indexed": len(rag.chunks),
        "ollama_reachable": ollama_ok,
    }