"""
Development Intelligence Platform – Application Configuration
============================================================
Loads environment variables with sensible defaults via Pydantic Settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Calculate absolute project root based on this file's location (app/config.py -> MZN)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # --- AI Model Settings ---
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "google/flan-t5-small"
    use_llm: bool = True
    llm_provider: str = "openrouter"  # Exclusive provider for stability
    failproof_llm: bool = True
    
    # --- API Keys ---
    gemini_api_key: str = "AIzaSyAEaPm5PZYjcr24guqEDvItKuWvyj7k1vo"
    openrouter_api_key: str = "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"

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 3000

    # --- Data Paths (Hardcoded to Absolute Paths) ---
    knowledge_base_dir: str = str(PROJECT_ROOT / "data" / "knowledge_docs")
    grants_csv_path: str = str(PROJECT_ROOT / "data" / "grants.csv")

    # --- Logging ---
    log_level: str = "INFO"

    # --- Retrieval ---
    top_k_results: int = 3
    chunk_size: int = 512
    chunk_overlap: int = 64

    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @property
    def knowledge_base_path(self) -> Path:
        return PROJECT_ROOT / "data" / "knowledge_docs"

    @property
    def grants_path(self) -> Path:
        return PROJECT_ROOT / "data" / "grants.csv"


settings = Settings()
