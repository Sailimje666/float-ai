from __future__ import annotations
import os
import time
from dataclasses import dataclass
from typing import Optional

import duckdb


def _ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Config:
    # Paths
    duckdb_path: str = os.environ.get("ARGO_DUCKDB_PATH", "data/argo.duckdb")
    faiss_index_path: str = os.environ.get("ARGO_FAISS_INDEX", "data/faiss.index")
    faiss_meta_path: str = os.environ.get("ARGO_FAISS_META", "data/faiss_meta.jsonl")
    data_dir: str = os.environ.get("ARGO_DATA_DIR", "data")

    # HF token optional; model is large so allow offline fallback
    hf_token: Optional[str] = os.environ.get("HUGGINGFACEHUB_API_TOKEN") or os.environ.get("HF_API_TOKEN")
    mistral_model_id: str = os.environ.get("MISTRAL_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")

    # Performance toggles
    in_memory_duckdb: bool = os.environ.get("ARGO_DUCKDB_IN_MEMORY", "0") == "1"

    # Spatial defaults
    srid: int = 4326


_duckdb_con: Optional[duckdb.DuckDBPyConnection] = None


def get_duckdb_connection(cfg: Optional[Config] = None) -> duckdb.DuckDBPyConnection:
    """
    Returns a singleton DuckDB connection and ensures spatial extension is available.
    """
    global _duckdb_con
    if _duckdb_con is not None:
        return _duckdb_con

    cfg = cfg or Config()
    db_target = ":memory:" if cfg.in_memory_duckdb else cfg.duckdb_path
    os.makedirs(os.path.dirname(cfg.duckdb_path), exist_ok=True)

    print(f"[{_ts()}] [v0] Opening DuckDB at {db_target}")
    _duckdb_con = duckdb.connect(db_target)
    try:
        # Enable spatial extension for geometry functions
        _duckdb_con.execute("INSTALL spatial;")
        _duckdb_con.execute("LOAD spatial;")
        print(f"[{_ts()}] [v0] DuckDB spatial extension loaded.")
    except Exception as e:
        # Continue without spatial if unavailable (fallback code will handle)
        print(f"[{_ts()}] [v0] Warning: Spatial extension not available: {e}")
    return _duckdb_con
