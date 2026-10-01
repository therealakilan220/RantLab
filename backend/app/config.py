"""Central settings. Everything can be overridden from the .env file at the repo root."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


# STUB_MODE=1 -> no AI models needed. Canned card, fake transcript, cheap word-hash embeddings.
# STUB_MODE=0 -> real Whisper + Ollama + MiniLM. Delete data/rantlab.db when you switch.
STUB_MODE = _flag("STUB_MODE", "1")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny | base | small
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Optional hosted-model fallback (Groq, OpenRouter, etc.). Off by default.
USE_CLOUD_API = _flag("USE_CLOUD_API", "0")
CLOUD_API_URL = os.getenv("CLOUD_API_URL", "https://api.groq.com/openai/v1").rstrip("/")
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY", "")
CLOUD_API_MODEL = os.getenv("CLOUD_API_MODEL", "llama-3.1-8b-instant")

# Cosine similarity needed to put two complaints in the same cluster.
CLUSTER_THRESHOLD = float(os.getenv("CLUSTER_THRESHOLD", "0.4" if STUB_MODE else "0.6"))

DB_PATH = os.getenv("DB_PATH", str(ROOT / "data" / "rantlab.db"))

MAX_AUDIO_BYTES = 10 * 1024 * 1024
MIN_AUDIO_BYTES = 1000
MAX_TEXT_CHARS = 2000
