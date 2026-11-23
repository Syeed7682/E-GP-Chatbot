"""
Global Configuration for e-GP Manual RAG System.
Configures data directories, models, indexing parameters, and retrieval settings.
Supports both persistent disk deployment (Render: /var/data/egp) and local dev.
Includes graceful fallback if /var/data is not mounted or has permission restrictions.
"""
import logging
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger("app.config")

# Base project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


def _resolve_data_dir() -> Path:
    """
    Safely resolves the data directory.
    If EGP_DATA_DIR (e.g. /var/data/egp on Render) is configured but not accessible
    (e.g. no persistent disk mounted), it gracefully falls back to the repository's
    local data directory without crashing the application on startup.
    """
    env_dir = os.getenv("EGP_DATA_DIR", "").strip()
    if env_dir:
        candidate = Path(env_dir)
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            # Verify write permissions with a temporary touch
            test_file = candidate / ".perm_check"
            test_file.touch(exist_ok=True)
            test_file.unlink(missing_ok=True)
            return candidate
        except (PermissionError, OSError) as e:
            logger.warning(
                "Configured EGP_DATA_DIR '%s' is not accessible (%s). Falling back to project data directory.",
                candidate,
                e,
            )

    default_dir = ROOT_DIR / "data"
    try:
        default_dir.mkdir(parents=True, exist_ok=True)
        return default_dir
    except (PermissionError, OSError) as e:
        tmp_dir = Path(tempfile.gettempdir()) / "egp_data"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        logger.warning("Default data directory '%s' inaccessible (%s). Using fallback: %s", default_dir, e, tmp_dir)
        return tmp_dir


DATA_DIR = _resolve_data_dir()

STRUCTURED_DIR = DATA_DIR / "structured"
RAW_DIR = STRUCTURED_DIR
PROCESSED_DIR = STRUCTURED_DIR / "metadata"
INDEX_DIR = STRUCTURED_DIR / "indexes"
IMAGE_DIR = STRUCTURED_DIR / "images"
CSV_DIR = ROOT_DIR / "csv_files"
EGP_MANUAL_CSV = CSV_DIR / "egp_manual_extracted.csv"
EGP_REG_MANUAL_CSV = CSV_DIR / "egp_registration_manual_extracted.csv"
EGP_EVAL_CSV = CSV_DIR / "egp_manual_extracted.csv"

# Ensure directories exist safely without raising PermissionError
for d in (STRUCTURED_DIR, RAW_DIR, PROCESSED_DIR, INDEX_DIR, IMAGE_DIR):
    try:
        d.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.debug("Notice: directory %s could not be created: %s", d, e)

# Models and Dimensions
TEXT_MODEL = os.getenv("TEXT_MODEL", "BAAI/bge-m3")
VISUAL_MODEL = os.getenv("VISUAL_MODEL", "google/siglip-base-patch16-224")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

TEXT_DIM = int(os.getenv("TEXT_DIM", "1024"))
VISUAL_DIM = int(os.getenv("VISUAL_DIM", "768"))

# Chunking Parameters
TEXT_CHUNK_SIZE = int(os.getenv("TEXT_CHUNK_SIZE", "1800"))
TEXT_CHUNK_OVERLAP = int(os.getenv("TEXT_CHUNK_OVERLAP", "240"))

# Retrieval Top-K Parameters
TEXT_TOP_K = int(os.getenv("TEXT_TOP_K", "3"))
QA_TOP_K = int(os.getenv("QA_TOP_K", "3"))
VISUAL_TOP_K = int(os.getenv("VISUAL_TOP_K", "2"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "3"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "3"))
FINAL_CONTEXT_K = int(os.getenv("FINAL_CONTEXT_K", "2"))

# Active index version
INDEX_VERSION = os.getenv("INDEX_VERSION", "active")
