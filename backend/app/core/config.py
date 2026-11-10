"""
Core Configuration Settings.
Loads and centralizes settings from environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "e-GP Official Manual Assistant"
    VERSION: str = "2.0.0"
    
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
    HF_TOKEN: str = os.getenv("HF_TOKEN", "").strip()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-VL-3B-Instruct").strip()
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "false").lower() in ("true", "1", "yes")
    
    # Embedding Settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3").strip()
    
    # Retrieval Settings
    VECTOR_DB: str = os.getenv("VECTOR_DB", "faiss").strip()
    TOP_K: int = int(os.getenv("TOP_K", "10"))
    
    # Host and Port Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1").strip()
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "3000"))
    CORS_ORIGINS: list[str] = [
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]
    
    # Directory Paths
    PROJECT_ROOT: Path = ROOT_DIR
    DATA_RAW_DIR: Path = ROOT_DIR / os.getenv("DATA_RAW_DIR", "data/raw")
    QA_DATA_PATH: Path = ROOT_DIR / os.getenv("QA_DATA_PATH", "data/raw/e-GP System Q&A.txt")
    QA_DOCX_PATH: Path = ROOT_DIR / os.getenv("QA_DOCX_PATH", "data/raw/e-GP System Q&A .docx")
    PROCESSED_DATA_PATH: Path = ROOT_DIR / os.getenv("PROCESSED_DATA_PATH", "data/processed/chunks.json")
    FAISS_INDEX_PATH: Path = ROOT_DIR / os.getenv("FAISS_INDEX_PATH", "data/faiss_index/index.faiss")
    FAISS_METADATA_PATH: Path = ROOT_DIR / os.getenv("FAISS_METADATA_PATH", "data/faiss_index/metadata.json")
    EXTRACTED_IMAGES_DIR: Path = ROOT_DIR / "data/extracted_images"

settings = Settings()
