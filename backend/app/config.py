"""
Global Configuration for e-GP Manual RAG System.
Configures data directories, models, indexing parameters, and retrieval settings.
Supports both persistent disk deployment (Render: /var/data/egp) and local dev.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# Base data directory: Render persistent disk or local fallback
DEFAULT_DATA_DIR = ROOT_DIR / "data"
EGP_DATA_DIR_ENV = os.getenv("EGP_DATA_DIR")
if EGP_DATA_DIR_ENV:
    DATA_DIR = Path(EGP_DATA_DIR_ENV)
else:
    DATA_DIR = DEFAULT_DATA_DIR

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "indexes"
IMAGE_DIR = DATA_DIR / "images"

# Ensure directories exist
for d in (RAW_DIR, PROCESSED_DIR, INDEX_DIR, IMAGE_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Models and Dimensions
TEXT_MODEL = os.getenv("TEXT_MODEL", "BAAI/bge-m3")
VISUAL_MODEL = os.getenv("VISUAL_MODEL", "google/siglip-base-patch16-224")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

TEXT_DIM = int(os.getenv("TEXT_DIM", "1024"))
VISUAL_DIM = int(os.getenv("VISUAL_DIM", "768"))

# Chunking Parameters
TEXT_CHUNK_SIZE = int(os.getenv("TEXT_CHUNK_SIZE", "450"))
TEXT_CHUNK_OVERLAP = int(os.getenv("TEXT_CHUNK_OVERLAP", "60"))

# Retrieval Top-K Parameters
TEXT_TOP_K = int(os.getenv("TEXT_TOP_K", "20"))
QA_TOP_K = int(os.getenv("QA_TOP_K", "20"))
VISUAL_TOP_K = int(os.getenv("VISUAL_TOP_K", "10"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "20"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "25"))
FINAL_CONTEXT_K = int(os.getenv("FINAL_CONTEXT_K", "7"))

# Active index version
INDEX_VERSION = os.getenv("INDEX_VERSION", "active")

